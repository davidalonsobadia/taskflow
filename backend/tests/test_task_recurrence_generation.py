"""Tests for generating the next occurrence when a recurring task completes (issue #11).

Completing a recurring task (``recurrence != none`` with a ``due_date``) via the
update endpoint spawns exactly one new task in the same list: incomplete, with
its ``due_date`` advanced by the recurrence interval and ``parent_task_id``
pointing at the completed task. The monthly rule advances by one calendar month
and clamps to the last valid day of the target month (Jan 31 -> Feb 28/29).
"""

from datetime import date

import pytest

from app.domains.lists.models import List as TaskList
from app.domains.tasks.models import RecurrenceEnum, Task


def _seed_list(db_session, user_id):
    task_list = TaskList(name="Inbox", user_id=user_id)
    db_session.add(task_list)
    db_session.commit()
    db_session.refresh(task_list)
    return task_list


def _seed_task(db_session, list_id, **overrides):
    fields = dict(
        title="Do the thing",
        description="A recurring chore",
        list_id=list_id,
        priority="high",
        due_date=date(2026, 3, 10),
        recurrence=RecurrenceEnum.daily,
        completed=False,
    )
    fields.update(overrides)
    task = Task(**fields)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


def _occurrences_of(db_session, parent_id):
    return (
        db_session.query(Task)
        .filter(Task.parent_task_id == parent_id)
        .all()
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "recurrence,expected_due",
    [
        (RecurrenceEnum.daily, date(2026, 3, 11)),
        (RecurrenceEnum.weekly, date(2026, 3, 17)),
        (RecurrenceEnum.monthly, date(2026, 4, 10)),
    ],
)
def test_completing_recurring_task_generates_next_occurrence(
    client, db_session, test_user, recurrence, expected_due
):
    """Completing a recurring task creates one occurrence with the advanced due_date."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session, task_list.id, recurrence=recurrence, due_date=date(2026, 3, 10)
    )

    response = client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})
    assert response.status_code == 200

    occurrences = _occurrences_of(db_session, task.id)
    assert len(occurrences) == 1
    occurrence = occurrences[0]
    assert occurrence.due_date == expected_due
    assert occurrence.completed is False
    assert occurrence.list_id == task_list.id
    assert occurrence.parent_task_id == task.id


@pytest.mark.integration
def test_occurrence_inherits_content_fields(client, db_session, test_user):
    """The generated occurrence copies title, description, priority and recurrence."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Water the plants",
        description="Kitchen and balcony",
        priority="low",
        recurrence=RecurrenceEnum.weekly,
    )

    client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})

    occurrence = _occurrences_of(db_session, task.id)[0]
    assert occurrence.title == "Water the plants"
    assert occurrence.description == "Kitchen and balcony"
    assert occurrence.priority == task.priority
    assert occurrence.recurrence == RecurrenceEnum.weekly


@pytest.mark.integration
def test_monthly_clamps_to_end_of_month(client, db_session, test_user):
    """Monthly from Jan 31 advances to Feb 28 in a non-leap year (2026)."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        recurrence=RecurrenceEnum.monthly,
        due_date=date(2026, 1, 31),
    )

    client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})

    occurrence = _occurrences_of(db_session, task.id)[0]
    assert occurrence.due_date == date(2026, 2, 28)


@pytest.mark.integration
def test_monthly_clamps_to_end_of_leap_february(client, db_session, test_user):
    """Monthly from Jan 31 lands on Feb 29 in a leap year (2028)."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        recurrence=RecurrenceEnum.monthly,
        due_date=date(2028, 1, 31),
    )

    client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})

    occurrence = _occurrences_of(db_session, task.id)[0]
    assert occurrence.due_date == date(2028, 2, 29)


@pytest.mark.integration
def test_completing_non_recurring_task_creates_no_occurrence(
    client, db_session, test_user
):
    """A non-recurring task completing does not spawn anything (unchanged behavior)."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session, task_list.id, recurrence=RecurrenceEnum.none, due_date=date(2026, 3, 10)
    )

    response = client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})
    assert response.status_code == 200

    assert _occurrences_of(db_session, task.id) == []
    assert db_session.query(Task).count() == 1


@pytest.mark.integration
def test_double_complete_generates_only_one_occurrence(client, db_session, test_user):
    """Re-saving an already-completed recurring task does not spawn a second occurrence."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(db_session, task_list.id, recurrence=RecurrenceEnum.daily)

    first = client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})
    assert first.status_code == 200

    # Completing again (still completed=True) must be a no-op for generation.
    second = client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})
    assert second.status_code == 200

    assert len(_occurrences_of(db_session, task.id)) == 1


@pytest.mark.integration
def test_generated_occurrence_visible_via_list_endpoint(client, db_session, test_user):
    """The new occurrence is returned by GET /tasks?list_id=... for the same list."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(db_session, task_list.id, recurrence=RecurrenceEnum.daily)

    client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})

    response = client.get(f"/api/v1/tasks?list_id={task_list.id}")
    assert response.status_code == 200
    body = response.json()

    occurrences = [t for t in body if t["parent_task_id"] == task.id]
    assert len(occurrences) == 1
    assert occurrences[0]["completed"] is False
    assert occurrences[0]["list_id"] == task_list.id

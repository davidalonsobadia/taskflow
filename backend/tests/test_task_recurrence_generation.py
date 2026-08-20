"""Tests for next-occurrence generation on recurring task completion (issue #11).

When a recurring task transitions to ``completed=True`` the service stages a new
task in the same list with the due_date advanced by one recurrence interval,
``completed=False`` and ``parent_task_id`` pointing at the source task. These
tests exercise that behavior through the HTTP API using the shared fixtures
(SQLite, ``TESTING=1``).
"""

from datetime import date

import pytest

from app.domains.lists.models import List as TaskList
from app.domains.tasks.models import RecurrenceEnum, Task
from app.domains.tasks.tasks import generate_next_occurrence_task


def _seed_list(db_session, user_id):
    task_list = TaskList(name="Inbox", user_id=user_id)
    db_session.add(task_list)
    db_session.commit()
    db_session.refresh(task_list)
    return task_list


def _seed_task(db_session, list_id, **kwargs):
    task = Task(list_id=list_id, **kwargs)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.mark.integration
@pytest.mark.parametrize(
    "recurrence, due_date, expected_due",
    [
        (RecurrenceEnum.daily, date(2026, 3, 15), date(2026, 3, 16)),
        (RecurrenceEnum.weekly, date(2026, 4, 10), date(2026, 4, 17)),
        (RecurrenceEnum.monthly, date(2026, 5, 15), date(2026, 6, 15)),
    ],
)
def test_completing_recurring_task_generates_next_occurrence(
    client, db_session, test_user, recurrence, due_date, expected_due
):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Recurring task",
        due_date=due_date,
        recurrence=recurrence,
    )

    resp = client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})
    assert resp.status_code == 200

    occurrences = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).all()
    )
    assert len(occurrences) == 1
    occurrence = occurrences[0]
    assert occurrence.due_date == expected_due
    assert occurrence.completed is False
    assert occurrence.list_id == task_list.id
    assert occurrence.recurrence == recurrence


@pytest.mark.integration
def test_occurrence_inherits_content_fields(client, db_session, test_user):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Water the plants",
        description="Living-room and balcony",
        priority="high",
        due_date=date(2026, 6, 1),
        recurrence=RecurrenceEnum.weekly,
    )

    resp = client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})
    assert resp.status_code == 200

    occurrence = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).one()
    )
    assert occurrence.title == "Water the plants"
    assert occurrence.description == "Living-room and balcony"
    assert occurrence.priority.value == "high"
    assert occurrence.recurrence == RecurrenceEnum.weekly


@pytest.mark.integration
def test_monthly_clamps_to_short_month_non_leap(client, db_session, test_user):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Month-end report",
        due_date=date(2026, 1, 31),
        recurrence=RecurrenceEnum.monthly,
    )

    resp = client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})
    assert resp.status_code == 200

    occurrence = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).one()
    )
    # 2026 is not a leap year -> Jan 31 clamps to Feb 28.
    assert occurrence.due_date == date(2026, 2, 28)


@pytest.mark.integration
def test_monthly_clamps_to_short_month_leap_year(client, db_session, test_user):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Month-end report",
        due_date=date(2028, 1, 31),
        recurrence=RecurrenceEnum.monthly,
    )

    resp = client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})
    assert resp.status_code == 200

    occurrence = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).one()
    )
    # 2028 is a leap year -> Jan 31 clamps to Feb 29.
    assert occurrence.due_date == date(2028, 2, 29)


@pytest.mark.integration
def test_monthly_rolls_over_year_boundary(client, db_session, test_user):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="December task",
        due_date=date(2026, 12, 15),
        recurrence=RecurrenceEnum.monthly,
    )

    resp = client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})
    assert resp.status_code == 200

    occurrence = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).one()
    )
    assert occurrence.due_date == date(2027, 1, 15)


@pytest.mark.integration
def test_completing_non_recurring_task_generates_nothing(
    client, db_session, test_user
):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="One-off task",
        due_date=date(2026, 7, 1),
        recurrence=RecurrenceEnum.none,
    )

    resp = client.put(f"/api/v1/tasks/{task.id}", json={"completed": True})
    assert resp.status_code == 200

    assert db_session.query(Task).filter(Task.parent_task_id.isnot(None)).count() == 0


@pytest.mark.integration
def test_double_complete_generates_single_occurrence(
    client, db_session, test_user
):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Idempotent task",
        due_date=date(2026, 8, 1),
        recurrence=RecurrenceEnum.daily,
    )

    assert client.put(f"/api/v1/tasks/{task.id}", json={"completed": True}).status_code == 200
    assert client.put(f"/api/v1/tasks/{task.id}", json={"completed": True}).status_code == 200

    occurrences = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).all()
    )
    assert len(occurrences) == 1


@pytest.mark.integration
def test_occurrence_visible_via_list_endpoint(client, db_session, test_user):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Listed task",
        due_date=date(2026, 9, 10),
        recurrence=RecurrenceEnum.daily,
    )

    assert client.put(f"/api/v1/tasks/{task.id}", json={"completed": True}).status_code == 200

    resp = client.get(f"/api/v1/tasks?list_id={task_list.id}")
    assert resp.status_code == 200
    tasks = resp.json()
    occurrences = [t for t in tasks if t["parent_task_id"] == task.id]
    assert len(occurrences) == 1
    assert occurrences[0]["due_date"] == "2026-09-11"
    assert occurrences[0]["completed"] is False


@pytest.mark.unit
def test_celery_task_generates_occurrence_directly(db_session, test_user):
    """Calling the Celery task directly creates the next occurrence.

    The task opens its own session from ``SessionLocal`` (rebound to the test
    engine by the fixtures) and commits the new occurrence itself.
    """
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Direct dispatch",
        due_date=date(2026, 10, 5),
        recurrence=RecurrenceEnum.weekly,
    )

    generate_next_occurrence_task(task.id)

    occurrences = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).all()
    )
    assert len(occurrences) == 1
    assert occurrences[0].due_date == date(2026, 10, 12)
    assert occurrences[0].completed is False
    assert occurrences[0].recurrence == RecurrenceEnum.weekly


@pytest.mark.unit
def test_celery_task_noop_for_missing_task(db_session, test_user):
    """The task is a safe no-op when the target task does not exist."""
    generate_next_occurrence_task(999999)

    assert db_session.query(Task).filter(Task.parent_task_id.isnot(None)).count() == 0

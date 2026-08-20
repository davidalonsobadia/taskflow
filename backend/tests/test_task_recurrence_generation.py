"""Tests for next-occurrence generation on recurring task completion (issue #11).

When a recurring task (``recurrence != none``) transitions to ``completed=True``,
the service spawns exactly one new task in the same list with its ``due_date``
advanced by the recurrence interval, ``completed=False`` and ``parent_task_id``
pointing at the source task. These tests exercise that behavior end-to-end
through the tasks endpoints (SQLite, ``TESTING=1``).

Month-end rule for ``monthly``: when the target month has fewer days than the
source day-of-month, the result is clamped to the last day of the target month
(e.g. Jan 31 -> Feb 28, or Feb 29 in a leap year).
"""

from datetime import date

import pytest

from app.domains.lists.models import List as TaskList
from app.domains.tasks.models import Task


def _seed_list(db_session, user_id):
    """Create a list owned by ``user_id`` and return it."""
    task_list = TaskList(name="Inbox", user_id=user_id)
    db_session.add(task_list)
    db_session.commit()
    db_session.refresh(task_list)
    return task_list


def _seed_task(db_session, list_id, **kwargs):
    """Create and persist a task with sensible defaults, return it."""
    task = Task(title=kwargs.pop("title", "Recurring task"), list_id=list_id, **kwargs)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.mark.integration
def test_complete_daily_generates_next_occurrence(client, db_session, test_user):
    """Completing a daily task creates one new task due +1 day."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        due_date=date(2026, 6, 15),
        recurrence="daily",
    )

    assert client.put(
        f"/api/v1/tasks/{task.id}", json={"completed": True}
    ).status_code == 200

    occurrences = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).all()
    )
    assert len(occurrences) == 1
    occurrence = occurrences[0]
    assert occurrence.due_date == date(2026, 6, 16)
    assert occurrence.completed is False
    assert occurrence.list_id == task_list.id
    assert occurrence.recurrence.value == "daily"


@pytest.mark.integration
def test_complete_weekly_generates_next_occurrence(client, db_session, test_user):
    """Completing a weekly task advances the due_date by 7 days."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        due_date=date(2026, 6, 15),
        recurrence="weekly",
    )

    assert client.put(
        f"/api/v1/tasks/{task.id}", json={"completed": True}
    ).status_code == 200

    occurrence = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).one()
    )
    assert occurrence.due_date == date(2026, 6, 22)


@pytest.mark.integration
def test_complete_monthly_generates_next_occurrence(client, db_session, test_user):
    """Completing a monthly task advances the due_date by one calendar month."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        due_date=date(2026, 6, 15),
        recurrence="monthly",
    )

    assert client.put(
        f"/api/v1/tasks/{task.id}", json={"completed": True}
    ).status_code == 200

    occurrence = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).one()
    )
    assert occurrence.due_date == date(2026, 7, 15)


@pytest.mark.integration
def test_monthly_clamps_to_month_end_non_leap(client, db_session, test_user):
    """Jan 31 monthly -> Feb 28 in a non-leap year."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        due_date=date(2026, 1, 31),
        recurrence="monthly",
    )

    assert client.put(
        f"/api/v1/tasks/{task.id}", json={"completed": True}
    ).status_code == 200

    occurrence = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).one()
    )
    assert occurrence.due_date == date(2026, 2, 28)


@pytest.mark.integration
def test_monthly_clamps_to_month_end_leap(client, db_session, test_user):
    """Jan 31 monthly -> Feb 29 in a leap year (2028)."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        due_date=date(2028, 1, 31),
        recurrence="monthly",
    )

    assert client.put(
        f"/api/v1/tasks/{task.id}", json={"completed": True}
    ).status_code == 200

    occurrence = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).one()
    )
    assert occurrence.due_date == date(2028, 2, 29)


@pytest.mark.integration
def test_monthly_across_year_boundary(client, db_session, test_user):
    """Dec 31 monthly -> Jan 31 of the following year."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        due_date=date(2026, 12, 31),
        recurrence="monthly",
    )

    assert client.put(
        f"/api/v1/tasks/{task.id}", json={"completed": True}
    ).status_code == 200

    occurrence = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).one()
    )
    assert occurrence.due_date == date(2027, 1, 31)


@pytest.mark.integration
def test_complete_non_recurring_generates_nothing(client, db_session, test_user):
    """Completing a non-recurring task creates no new task."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        due_date=date(2026, 6, 15),
        recurrence="none",
    )

    assert client.put(
        f"/api/v1/tasks/{task.id}", json={"completed": True}
    ).status_code == 200

    assert db_session.query(Task).count() == 1


@pytest.mark.integration
def test_double_complete_generates_one_occurrence(client, db_session, test_user):
    """Re-saving an already-completed recurring task spawns no extra occurrence."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        due_date=date(2026, 6, 15),
        recurrence="daily",
    )

    assert client.put(
        f"/api/v1/tasks/{task.id}", json={"completed": True}
    ).status_code == 200
    assert client.put(
        f"/api/v1/tasks/{task.id}", json={"completed": True}
    ).status_code == 200

    occurrences = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).all()
    )
    assert len(occurrences) == 1


@pytest.mark.integration
def test_occurrence_inherits_content_fields(client, db_session, test_user):
    """The occurrence inherits title, description, priority and recurrence."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Weekly review",
        description="My description",
        priority="high",
        due_date=date(2026, 6, 15),
        recurrence="weekly",
    )

    assert client.put(
        f"/api/v1/tasks/{task.id}", json={"completed": True}
    ).status_code == 200

    occurrence = (
        db_session.query(Task).filter(Task.parent_task_id == task.id).one()
    )
    assert occurrence.title == "Weekly review"
    assert occurrence.description == "My description"
    assert occurrence.priority.value == "high"
    assert occurrence.recurrence.value == "weekly"


@pytest.mark.integration
def test_occurrence_visible_via_list_endpoint(client, db_session, test_user):
    """The generated occurrence is returned by GET /tasks?list_id=..."""
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        due_date=date(2026, 6, 15),
        recurrence="daily",
    )

    assert client.put(
        f"/api/v1/tasks/{task.id}", json={"completed": True}
    ).status_code == 200

    response = client.get(f"/api/v1/tasks?list_id={task_list.id}")
    assert response.status_code == 200
    body = response.json()
    parents = [t["parent_task_id"] for t in body]
    assert task.id in parents
    for t in body:
        assert t["list_id"] == task_list.id

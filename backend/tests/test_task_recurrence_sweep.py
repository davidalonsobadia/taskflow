"""Tests for the scheduled recurring-occurrence sweep (issue #13).

``tasks.sweep_due_recurrences`` runs periodically (via Celery beat) and generates
the next occurrence for recurring, uncompleted tasks whose ``due_date`` is today
or earlier and that do not already have a generated successor. These tests call
the task function directly with seeded data (SQLite, ``TESTING=1``).
"""

from datetime import date, timedelta

import pytest

from app.domains.lists.models import List as TaskList
from app.domains.tasks.models import RecurrenceEnum, Task
from app.domains.tasks.tasks import sweep_due_recurrences

TODAY = date.today()
# "Overdue" anchor whose weekly/monthly successor still lands in the future, so a
# single advance closes the gap and re-running the sweep is a no-op.
RECENT_PAST = TODAY - timedelta(days=3)
FUTURE = TODAY + timedelta(days=10)


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


@pytest.mark.unit
def test_sweep_generates_occurrence_for_due_recurring_task(db_session, test_user):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Daily due today",
        due_date=TODAY,
        recurrence=RecurrenceEnum.daily,
    )

    generated = sweep_due_recurrences()

    assert generated == 1
    occurrences = db_session.query(Task).filter(Task.parent_task_id == task.id).all()
    assert len(occurrences) == 1
    occurrence = occurrences[0]
    assert occurrence.due_date == TODAY + timedelta(days=1)
    assert occurrence.completed is False
    assert occurrence.list_id == task_list.id
    assert occurrence.recurrence == RecurrenceEnum.daily


@pytest.mark.unit
def test_sweep_generates_occurrence_for_overdue_recurring_task(db_session, test_user):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Overdue weekly",
        due_date=RECENT_PAST,
        recurrence=RecurrenceEnum.weekly,
    )

    generated = sweep_due_recurrences()

    assert generated == 1
    occurrence = db_session.query(Task).filter(Task.parent_task_id == task.id).one()
    assert occurrence.due_date == RECENT_PAST + timedelta(days=7)
    assert occurrence.completed is False


@pytest.mark.unit
def test_sweep_is_idempotent(db_session, test_user):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Overdue weekly",
        due_date=RECENT_PAST,
        recurrence=RecurrenceEnum.weekly,
    )

    first = sweep_due_recurrences()
    second = sweep_due_recurrences()

    assert first == 1
    assert second == 0
    occurrences = db_session.query(Task).filter(Task.parent_task_id == task.id).all()
    assert len(occurrences) == 1


@pytest.mark.unit
def test_sweep_ignores_future_dated_recurring_task(db_session, test_user):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Future daily",
        due_date=FUTURE,
        recurrence=RecurrenceEnum.daily,
    )

    generated = sweep_due_recurrences()

    assert generated == 0
    assert db_session.query(Task).filter(Task.parent_task_id == task.id).count() == 0


@pytest.mark.unit
def test_sweep_ignores_non_recurring_overdue_task(db_session, test_user):
    task_list = _seed_list(db_session, test_user.id)
    _seed_task(
        db_session,
        task_list.id,
        title="Overdue one-off",
        due_date=RECENT_PAST,
        recurrence=RecurrenceEnum.none,
    )

    generated = sweep_due_recurrences()

    assert generated == 0
    assert db_session.query(Task).filter(Task.parent_task_id.isnot(None)).count() == 0


@pytest.mark.unit
def test_sweep_ignores_completed_recurring_task(db_session, test_user):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Completed overdue daily",
        due_date=RECENT_PAST,
        recurrence=RecurrenceEnum.daily,
        completed=True,
    )

    generated = sweep_due_recurrences()

    assert generated == 0
    assert db_session.query(Task).filter(Task.parent_task_id == task.id).count() == 0


@pytest.mark.unit
def test_sweep_ignores_recurring_task_without_due_date(db_session, test_user):
    task_list = _seed_list(db_session, test_user.id)
    task = _seed_task(
        db_session,
        task_list.id,
        title="Daily without due date",
        due_date=None,
        recurrence=RecurrenceEnum.daily,
    )

    generated = sweep_due_recurrences()

    assert generated == 0
    assert db_session.query(Task).filter(Task.parent_task_id == task.id).count() == 0


@pytest.mark.unit
def test_sweep_generates_one_occurrence_each_for_multiple_tasks(db_session, test_user):
    task_list = _seed_list(db_session, test_user.id)
    first = _seed_task(
        db_session,
        task_list.id,
        title="Overdue weekly",
        due_date=RECENT_PAST,
        recurrence=RecurrenceEnum.weekly,
    )
    second = _seed_task(
        db_session,
        task_list.id,
        title="Overdue monthly",
        due_date=TODAY - timedelta(days=5),
        recurrence=RecurrenceEnum.monthly,
    )

    generated = sweep_due_recurrences()

    assert generated == 2
    assert db_session.query(Task).filter(Task.parent_task_id == first.id).count() == 1
    assert db_session.query(Task).filter(Task.parent_task_id == second.id).count() == 1

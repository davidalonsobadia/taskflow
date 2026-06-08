"""Tests for the recurrence schema/contract layer on the tasks endpoints.

These cover the behavior added by issue #10: the tasks API accepts and returns
a ``recurrence`` rule, exposes ``parent_task_id`` on responses, and rejects a
non-``none`` recurrence that has no ``due_date`` to anchor it. This is the
contract layer only — no next-occurrence generation.
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


@pytest.mark.integration
def test_create_with_recurrence_and_due_date(client, db_session, test_user):
    """Creating with recurrence=weekly + a due_date persists and echoes it."""
    task_list = _seed_list(db_session, test_user.id)

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Weekly review",
            "list_id": task_list.id,
            "due_date": "2026-06-15",
            "recurrence": "weekly",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["recurrence"] == "weekly"
    assert body["parent_task_id"] is None

    db_task = db_session.query(Task).filter(Task.id == body["id"]).first()
    assert db_task.recurrence.value == "weekly"


@pytest.mark.integration
def test_create_recurrence_without_due_date_is_rejected(
    client, db_session, test_user
):
    """A non-none recurrence with no due_date returns 400."""
    task_list = _seed_list(db_session, test_user.id)

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Daily standup",
            "list_id": task_list.id,
            "recurrence": "daily",
        },
    )

    assert response.status_code == 400


@pytest.mark.integration
def test_create_defaults_recurrence_to_none(client, db_session, test_user):
    """Omitting recurrence on create defaults it to none."""
    task_list = _seed_list(db_session, test_user.id)

    response = client.post(
        "/api/v1/tasks",
        json={"title": "One-off task", "list_id": task_list.id},
    )

    assert response.status_code == 201
    assert response.json()["recurrence"] == "none"


@pytest.mark.integration
def test_update_recurrence_persists(client, db_session, test_user):
    """Updating recurrence to monthly (with a due date) is persisted."""
    task_list = _seed_list(db_session, test_user.id)
    task = Task(
        title="Pay rent",
        list_id=task_list.id,
        due_date=date(2026, 7, 1),
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.put(
        f"/api/v1/tasks/{task.id}",
        json={"recurrence": "monthly"},
    )

    assert response.status_code == 200
    assert response.json()["recurrence"] == "monthly"

    db_session.refresh(task)
    assert task.recurrence.value == "monthly"


@pytest.mark.integration
def test_update_recurrence_without_due_date_is_rejected(
    client, db_session, test_user
):
    """Setting a non-none recurrence on a task without a due_date returns 400."""
    task_list = _seed_list(db_session, test_user.id)
    task = Task(title="No due date", list_id=task_list.id)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.put(
        f"/api/v1/tasks/{task.id}",
        json={"recurrence": "weekly"},
    )

    assert response.status_code == 400


@pytest.mark.integration
def test_update_without_recurrence_leaves_it_unchanged(
    client, db_session, test_user
):
    """Omitting recurrence on update leaves the existing value unchanged."""
    task_list = _seed_list(db_session, test_user.id)
    task = Task(
        title="Weekly task",
        list_id=task_list.id,
        due_date=date(2026, 7, 1),
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    # Set it to weekly first.
    client.put(f"/api/v1/tasks/{task.id}", json={"recurrence": "weekly"})

    # Update an unrelated field; recurrence should survive.
    response = client.put(
        f"/api/v1/tasks/{task.id}",
        json={"title": "Weekly task renamed"},
    )

    assert response.status_code == 200
    assert response.json()["recurrence"] == "weekly"

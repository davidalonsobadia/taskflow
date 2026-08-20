"""Celery tasks for the tasks domain.

Currently hosts next-occurrence generation for recurring tasks. Completing a
recurring task dispatches ``generate_next_occurrence_task`` via ``.delay(...)``
from :class:`~app.domains.tasks.service.TasksService`, so the extra DB work
happens on the worker instead of inline in the request.
"""
import logging
from datetime import date

# Import every ORM model module so SQLAlchemy's mapper registry is fully
# populated before the first query runs. A fresh Celery worker only imports the
# autodiscovered task modules, so string-based relationships (e.g.
# ``List.user -> "User"``) would fail to resolve unless the modules that define
# those models are imported here. ADD any new domain's model module below.
import app.domains.api_clients.models  # noqa: F401
import app.domains.auth.models  # noqa: F401
import app.domains.lists.models  # noqa: F401
import app.domains.tasks.models  # noqa: F401
from app.celery_app import celery
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


@celery.task(name="tasks.generate_next_occurrence")
def generate_next_occurrence_task(task_id: int) -> None:
    """Generate the next occurrence of a recurring task.

    The request-scoped session is gone by the time this runs, so the task opens
    its own session from ``SessionLocal``, loads the completed task, stages its
    next occurrence via the reusable ``TasksService.generate_next_occurrence``
    method and commits. The session is always closed in ``finally``.

    Args:
        task_id: ID of the task whose completion triggered generation.
    """
    # Imported inside the function to avoid a circular import: ``service.py``
    # imports this module at module level to dispatch the task, so importing the
    # service at module level here would create a cycle.
    from app.domains.tasks.models import Task
    from app.domains.tasks.service import TasksService

    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            logger.warning(
                "generate_next_occurrence: task %s not found; skipping", task_id
            )
            return

        occurrence = TasksService(db).generate_next_occurrence(task)
        db.commit()
        if occurrence is not None:
            logger.info(
                "Generated next occurrence of task %s (new due_date %s)",
                task_id,
                occurrence.due_date,
            )
    except Exception:
        db.rollback()
        logger.exception("Failed to generate next occurrence of task %s", task_id)
        raise
    finally:
        db.close()


@celery.task(name="tasks.sweep_due_recurrences")
def sweep_due_recurrences(limit: int = 500) -> int:
    """Generate the next occurrence for due-or-overdue recurring tasks on schedule.

    Completing a recurring task already spawns its successor; this periodic sweep
    covers the case where the user never ticks it off. It finds recurring,
    uncompleted tasks whose ``due_date`` is today or earlier and that do not yet
    have a generated successor, then stages one next occurrence for each.

    Successor detection uses ``parent_task_id``: a task is skipped when a child
    occurrence with a later ``due_date`` already exists, which keeps the sweep
    idempotent — running it twice in a row creates no duplicates.

    The server date (UTC, matching the existing recurrence/overdue logic) is used;
    per-user timezones are out of scope. Work is bounded to ``limit`` tasks per
    run so a large backlog cannot make a single sweep unbounded.

    Args:
        limit: Maximum number of tasks to process in one sweep.

    Returns:
        The number of occurrences generated.
    """
    # Imported inside the function to avoid a circular import (see the note on
    # ``generate_next_occurrence_task`` above): ``service.py`` imports this module.
    from sqlalchemy.orm import aliased

    from app.domains.tasks.models import RecurrenceEnum, Task
    from app.domains.tasks.service import TasksService

    db = SessionLocal()
    generated = 0
    try:
        today = date.today()
        service = TasksService(db)

        # A successor already exists when a child occurrence points at this task
        # via ``parent_task_id`` and has a later due_date (generated occurrences
        # always advance the due_date). Such tasks are excluded so the sweep is
        # idempotent and does not pile up duplicates.
        successor = aliased(Task)
        has_successor = (
            db.query(successor.id)
            .filter(
                successor.parent_task_id == Task.id,
                successor.due_date.isnot(None),
                successor.due_date > Task.due_date,
            )
            .exists()
        )

        candidates = (
            db.query(Task)
            .filter(
                Task.recurrence != RecurrenceEnum.none,
                Task.completed.is_(False),
                Task.due_date.isnot(None),
                Task.due_date <= today,
                ~has_successor,
            )
            .order_by(Task.due_date.asc())
            .limit(limit)
            .all()
        )

        for task in candidates:
            occurrence = service.generate_next_occurrence(task)
            if occurrence is not None:
                generated += 1

        db.commit()
        logger.info(
            "sweep_due_recurrences: scanned %d candidate(s), generated %d occurrence(s)",
            len(candidates),
            generated,
        )
        return generated
    except Exception:
        db.rollback()
        logger.exception("sweep_due_recurrences failed")
        raise
    finally:
        db.close()

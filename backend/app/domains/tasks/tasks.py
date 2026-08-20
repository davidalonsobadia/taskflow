"""Celery tasks for the tasks domain.

Currently hosts next-occurrence generation for recurring tasks. Completing a
recurring task dispatches ``generate_next_occurrence_task`` via ``.delay(...)``
from :class:`~app.domains.tasks.service.TasksService`, so the extra DB work
happens on the worker instead of inline in the request.
"""
import logging

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

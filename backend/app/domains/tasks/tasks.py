"""
Celery tasks for the tasks domain.
"""
import logging

# Import every ORM model module so SQLAlchemy's mapper registry is complete
# before any query runs. A fresh Celery worker only loads the autodiscovered
# task modules; without these imports the string-based relationships (e.g.
# ``List.user -> "User"``) cannot be resolved and the first query raises a
# mapper-initialization error. See issue #12.
import app.domains.api_clients.models  # noqa: F401
import app.domains.auth.models  # noqa: F401
import app.domains.lists.models  # noqa: F401
import app.domains.tasks.models  # noqa: F401
from app.celery_app import celery
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


@celery.task(name="tasks.generate_next_occurrence")
def generate_next_occurrence_task(task_id: int) -> None:
    """
    Generate the next occurrence of a recurring task.

    Runs in the Celery worker, so it opens its own DB session from
    ``SessionLocal`` (the request-scoped ``get_db`` generator is not available
    here), loads the task, delegates to ``TasksService.generate_next_occurrence``
    and commits. The session is always closed in the ``finally`` block.

    Args:
        task_id: ID of the just-completed recurring task to advance.
    """
    # Local import to avoid a circular import: ``service.py`` imports this module
    # at module level to dispatch the task via ``.delay(...)``. Keep this import
    # inside the function — moving it to module level reintroduces the cycle.
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

        service = TasksService(db)
        service.generate_next_occurrence(task)
        db.commit()
        logger.info("Generated next occurrence for task %s", task_id)
    except Exception:
        db.rollback()
        logger.exception("Failed to generate next occurrence of task %s", task_id)
        raise
    finally:
        db.close()

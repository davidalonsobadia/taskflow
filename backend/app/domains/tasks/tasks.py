"""
Celery tasks for the tasks domain
"""
import logging

from app.celery_app import celery
from app.db.session import SessionLocal
from app.domains.tasks.models import Task

logger = logging.getLogger(__name__)


@celery.task(name="tasks.generate_next_occurrence")
def generate_next_occurrence_task(task_id: int):
    """
    Generate the next occurrence of a recurring task asynchronously.

    Loads the source task by id in a dedicated DB session and delegates to
    ``TasksService.generate_next_occurrence``. Under ``TESTING=1`` Celery runs
    eager, so this executes synchronously.

    Args:
        task_id: ID of the completed recurring task to generate from.
    """
    # Imported here to avoid a circular import with the service module.
    from app.domains.tasks.service import TasksService

    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            logger.warning(
                f"generate_next_occurrence: task {task_id} not found, skipping"
            )
            return

        occurrence = TasksService(db).generate_next_occurrence(task)
        if occurrence is not None:
            db.commit()
            logger.info(
                f"Generated next occurrence of task {task_id} due {occurrence.due_date}"
            )
    except Exception as e:
        db.rollback()
        logger.error(
            f"Failed to generate next occurrence of task {task_id}: {str(e)}"
        )
        raise
    finally:
        db.close()

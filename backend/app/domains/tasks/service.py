from datetime import date, timedelta
from typing import List as ListType
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domains.lists.models import List
from app.domains.tasks.models import Task
from app.domains.tasks.schemas import (
    PriorityEnum,
    RecurrenceEnum,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.domains.tasks.tasks import generate_next_occurrence_task


class TasksService:
    def __init__(self, db: Session):
        self.db = db

    def verify_list_ownership(self, list_id: int, user_id: int) -> List:
        """
        Verify that the list belongs to the user
        """
        db_list = self.db.query(List).filter(
            List.id == list_id,
            List.user_id == user_id
        ).first()

        if not db_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="List not found or access denied"
            )

        return db_list

    def get_tasks_by_list(
        self,
        list_id: int,
        user_id: int,
        completed: Optional[bool] = None,
        priority: Optional[PriorityEnum] = None,
        due_after: Optional[date] = None,
        due_before: Optional[date] = None,
        overdue: Optional[bool] = None
    ) -> ListType[TaskResponse]:
        """
        Get all tasks for a specific list with optional completed, priority,
        due-date range and overdue filters
        """
        # Verify list ownership
        self.verify_list_ownership(list_id, user_id)

        # Build query
        query = self.db.query(Task).join(List).filter(
            Task.list_id == list_id,
            List.user_id == user_id
        )

        # Apply completed filter if provided
        if completed is not None:
            query = query.filter(Task.completed == completed)

        # Apply priority filter if provided
        if priority is not None:
            query = query.filter(Task.priority == priority)

        # Apply due_date range filters if provided. Tasks with a null due_date
        # are excluded when either bound is set.
        if due_after is not None:
            query = query.filter(Task.due_date.isnot(None), Task.due_date >= due_after)

        if due_before is not None:
            query = query.filter(Task.due_date.isnot(None), Task.due_date <= due_before)

        # Apply overdue filter if requested: tasks past due are those with a
        # due_date strictly before today (server date) that are not completed.
        # Tasks with a null due_date are never considered overdue.
        if overdue:
            query = query.filter(
                Task.due_date.isnot(None),
                Task.due_date < date.today(),
                Task.completed.is_(False)
            )

        # Order by: incomplete first, then by due date, then by priority
        tasks = query.order_by(
            Task.completed.asc(),
            Task.due_date.asc().nullslast(),
            Task.priority.desc()
        ).all()

        return [TaskResponse.model_validate(task) for task in tasks]

    def get_task_by_id(self, task_id: int, user_id: int) -> TaskResponse:
        """
        Get a specific task by ID
        """
        task = self.db.query(Task).join(List).filter(
            Task.id == task_id,
            List.user_id == user_id
        ).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return TaskResponse.model_validate(task)

    def create_task(self, task_data: TaskCreate, user_id: int) -> TaskResponse:
        """
        Create a new task
        """
        # Verify list ownership
        self.verify_list_ownership(task_data.list_id, user_id)

        # A recurring task needs a due_date to anchor the recurrence rule.
        if task_data.recurrence != RecurrenceEnum.none and task_data.due_date is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A recurring task requires a due_date"
            )

        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            list_id=task_data.list_id,
            priority=task_data.priority,
            due_date=task_data.due_date,
            recurrence=task_data.recurrence,
            completed=False
        )

        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)

        return TaskResponse.model_validate(db_task)

    def update_task(self, task_id: int, task_data: TaskUpdate, user_id: int) -> TaskResponse:
        """
        Update an existing task
        """
        # Get task and verify ownership through list
        db_task = self.db.query(Task).join(List).filter(
            Task.id == task_id,
            List.user_id == user_id
        ).first()

        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Capture the completion state before the update so we can detect the
        # false -> true transition that triggers next-occurrence generation.
        was_completed = db_task.completed

        # Update only provided fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)

        # A recurring task needs a due_date to anchor the recurrence rule.
        # Validate the resulting state after applying the partial update.
        if db_task.recurrence != RecurrenceEnum.none and db_task.due_date is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A recurring task requires a due_date"
            )

        # On the transition into completion, generate the next occurrence for a
        # recurring task. Guarding on the transition keeps this idempotent: a
        # re-save of an already-completed task spawns nothing. Capture the flag
        # and id before commit so they survive attribute expiration.
        should_generate = not was_completed and db_task.completed
        task_id = db_task.id

        self.db.commit()

        # Dispatch generation only after the completion is committed, so the
        # worker's own session sees the persisted row. The task is a safe no-op
        # for non-recurring tasks (generate_next_occurrence returns None). Under
        # TESTING=1 Celery runs eager, so this executes synchronously.
        if should_generate:
            generate_next_occurrence_task.delay(task_id)

        self.db.refresh(db_task)

        return TaskResponse.model_validate(db_task)

    def generate_next_occurrence(self, task: Task) -> Optional[Task]:
        """
        Stage the next occurrence of a recurring task in the same list.

        Returns the new (uncommitted) task, or None if ``task`` is not
        recurring or has no due_date. The caller commits the transaction.
        """
        if task.recurrence == RecurrenceEnum.none or task.due_date is None:
            return None

        occurrence = Task(
            title=task.title,
            description=task.description,
            list_id=task.list_id,
            priority=task.priority,
            due_date=self._advance_due_date(task.due_date, task.recurrence),
            recurrence=task.recurrence,
            completed=False,
            parent_task_id=task.id,
        )
        self.db.add(occurrence)
        return occurrence

    @staticmethod
    def _advance_due_date(due_date: date, recurrence: RecurrenceEnum) -> date:
        """Advance ``due_date`` by one recurrence interval."""
        if recurrence == RecurrenceEnum.daily:
            return due_date + timedelta(days=1)
        if recurrence == RecurrenceEnum.weekly:
            return due_date + timedelta(days=7)
        if recurrence == RecurrenceEnum.monthly:
            return TasksService._add_one_month(due_date)
        raise ValueError(f"Unhandled recurrence: {recurrence}")

    @staticmethod
    def _add_one_month(due_date: date) -> date:
        """
        Add one calendar month, clamping to the last valid day of the target
        month (e.g. Jan 31 -> Feb 28, or Feb 29 in a leap year).
        """
        year = due_date.year + due_date.month // 12
        month = due_date.month % 12 + 1
        # Last day of the target month: day before the first of the following one.
        next_year = year + month // 12
        next_month = month % 12 + 1
        last_day = (date(next_year, next_month, 1) - timedelta(days=1)).day
        return date(year, month, min(due_date.day, last_day))

    def delete_task(self, task_id: int, user_id: int) -> None:
        """
        Delete a task
        """
        # Get task and verify ownership through list
        db_task = self.db.query(Task).join(List).filter(
            Task.id == task_id,
            List.user_id == user_id
        ).first()

        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        self.db.delete(db_task)
        self.db.commit()

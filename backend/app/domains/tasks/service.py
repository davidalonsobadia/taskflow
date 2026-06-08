from datetime import date
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

        self.db.commit()
        self.db.refresh(db_task)

        return TaskResponse.model_validate(db_task)

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

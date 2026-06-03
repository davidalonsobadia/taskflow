from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List as ListType, Optional
from app.domains.tasks.models import Task
from app.domains.tasks.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.domains.lists.models import List

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
        completed: Optional[bool] = None
    ) -> ListType[TaskResponse]:
        """
        Get all tasks for a specific list with optional completed filter
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

        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            list_id=task_data.list_id,
            priority=task_data.priority,
            due_date=task_data.due_date,
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
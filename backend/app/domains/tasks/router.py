from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.domains.auth.utils import get_verified_user
from app.domains.auth.models import User
from app.domains.tasks.schemas import TaskCreate, TaskUpdate, TaskResponse, MessageResponse
from app.domains.tasks.service import TasksService

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("", response_model=List[TaskResponse])
def get_tasks(
    list_id: int = Query(..., description="ID of the list to get tasks from"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    """
    Get all tasks for a specific list. Optional filter by completion status.

    - **list_id**: Required. The ID of the list to get tasks from
    - **completed**: Optional. Filter tasks by completion status (true/false)
    """
    tasks_service = TasksService(db)
    return tasks_service.get_tasks_by_list(list_id, current_user.id, completed)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    """
    Get a specific task by ID.
    """
    tasks_service = TasksService(db)
    return tasks_service.get_task_by_id(task_id, current_user.id)

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    """
    Create a new task in a list.

    The list must belong to the authenticated user.
    """
    tasks_service = TasksService(db)
    return tasks_service.create_task(task_data, current_user.id)

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    """
    Update an existing task. Only provided fields will be updated.

    Can be used to update title, description, priority, due_date, or completion status.
    """
    tasks_service = TasksService(db)
    return tasks_service.update_task(task_id, task_data, current_user.id)

@router.delete("/{task_id}", response_model=MessageResponse)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    """
    Delete a task.
    """
    tasks_service = TasksService(db)
    tasks_service.delete_task(task_id, current_user.id)
    return {"message": "Task deleted successfully"}
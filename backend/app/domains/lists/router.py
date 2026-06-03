from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.domains.auth.utils import get_verified_user
from app.domains.auth.models import User
from . import schemas, service

router = APIRouter(prefix="/lists", tags=["lists"])


@router.get("", response_model=List[schemas.ListResponse])
def get_lists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    """
    Get all lists for the authenticated user.
    """
    lists_service = service.ListsService(db)
    lists = lists_service.get_all_lists(current_user.id)

    # Convert to response schema
    return [
        schemas.ListResponse(
            id=list_obj.id,
            name=list_obj.name,
            color=list_obj.color,
            description=list_obj.description,
            user_id=list_obj.user_id,
            task_count=0,  # TODO: Add task counting when Task model exists
            completed_count=0,
            created_at=list_obj.created_at,
            updated_at=list_obj.updated_at
        )
        for list_obj in lists
    ]


@router.get("/{list_id}", response_model=schemas.ListResponse)
def get_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    """
    Get a specific list by ID.
    """
    lists_service = service.ListsService(db)
    list_obj = lists_service.get_list_by_id(list_id, current_user.id)

    if not list_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )

    return schemas.ListResponse(
        id=list_obj.id,
        name=list_obj.name,
        color=list_obj.color,
        description=list_obj.description,
        user_id=list_obj.user_id,
        task_count=0,  # TODO: Add task counting when Task model exists
        completed_count=0,
        created_at=list_obj.created_at,
        updated_at=list_obj.updated_at
    )


@router.post("", response_model=schemas.ListResponse, status_code=status.HTTP_201_CREATED)
def create_list(
    list_data: schemas.ListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    """
    Create a new list for the authenticated user.
    """
    lists_service = service.ListsService(db)
    list_obj = lists_service.create_list(list_data, current_user.id)

    return schemas.ListResponse(
        id=list_obj.id,
        name=list_obj.name,
        color=list_obj.color,
        description=list_obj.description,
        user_id=list_obj.user_id,
        task_count=0,
        completed_count=0,
        created_at=list_obj.created_at,
        updated_at=list_obj.updated_at
    )

@router.put("/{list_id}", response_model=schemas.ListResponse)
def update_list(
    list_id: int,
    list_data: schemas.ListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    """
    Update an existing list. Only provided fields will be updated.
    """
    lists_service = service.ListsService(db)
    list_obj = lists_service.update_list(list_id, list_data, current_user.id)

    return schemas.ListResponse(
        id=list_obj.id,
        name=list_obj.name,
        color=list_obj.color,
        description=list_obj.description,
        user_id=list_obj.user_id,
        task_count=0,
        completed_count=0,
        created_at=list_obj.created_at,
        updated_at=list_obj.updated_at
    )


@router.delete("/{list_id}", response_model=schemas.MessageResponse)
def delete_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user)
):
    """
    Delete a list.
    """
    lists_service = service.ListsService(db)
    lists_service.delete_list(list_id, current_user.id)
    return {"message": "List deleted successfully"}
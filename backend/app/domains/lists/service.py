from typing import List as ListType, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from . import models, schemas


class ListsService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_lists(self, user_id: int) -> ListType[models.List]:
        """
        Get all lists for a user
        """
        return self.db.query(models.List).filter(
            models.List.user_id == user_id
        ).order_by(models.List.created_at.desc()).all()

    def get_list_by_id(self, list_id: int, user_id: int) -> Optional[models.List]:
        """
        Get a specific list by ID
        """
        return self.db.query(models.List).filter(
            models.List.id == list_id,
            models.List.user_id == user_id
        ).first()

    def create_list(self, payload: schemas.ListCreate, user_id: int) -> models.List:
        """
        Create a new list
        """
        db_list = models.List(
            name=payload.name,
            color=payload.color,
            description=payload.description,
            user_id=user_id
        )

        self.db.add(db_list)
        self.db.commit()
        self.db.refresh(db_list)

        return db_list

    def update_list(self, list_id: int, payload: schemas.ListUpdate, user_id: int) -> models.List:
        """
        Update an existing list
        """
        db_list = self.db.query(models.List).filter(
            models.List.id == list_id,
            models.List.user_id == user_id
        ).first()

        if not db_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="List not found"
            )

        # Update only provided fields
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_list, field, value)

        self.db.commit()
        self.db.refresh(db_list)

        return db_list

    def delete_list(self, list_id: int, user_id: int) -> None:
        """
        Delete a list
        """
        db_list = self.db.query(models.List).filter(
            models.List.id == list_id,
            models.List.user_id == user_id
        ).first()

        if not db_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="List not found"
            )

        self.db.delete(db_list)
        self.db.commit()
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class RecurrenceEnum(str, Enum):
    none = "none"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    list_id: int
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[date] = None
    recurrence: RecurrenceEnum = RecurrenceEnum.none

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[date] = None
    completed: Optional[bool] = None
    recurrence: Optional[RecurrenceEnum] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    list_id: int
    priority: str
    due_date: Optional[date]
    completed: bool
    recurrence: str
    parent_task_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    message: str

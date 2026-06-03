from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ListCreate(BaseModel):
    name: str
    color: str = "#dc2626"  # Default dark red
    description: Optional[str] = None

class ListUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None

class ListResponse(BaseModel):
    id: int
    name: str
    color: str
    description: Optional[str]
    user_id: int
    task_count: int = 0
    completed_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    message: str
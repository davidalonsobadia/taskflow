from pydantic import BaseModel, computed_field
from typing import Optional

class UserRegisteredPayload(BaseModel):
    user_id: int
    email: str
    role: str
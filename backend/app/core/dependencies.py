# app/core/dependencies.py
from fastapi import Depends, HTTPException
from app.core.schemas import UserTokenPayload
from app.core.security import get_current_user
from app.domains.identity.models import User, UserRole

def require_verified_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User not verified")
    return user

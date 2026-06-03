# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from app import logger

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.core.schemas import UserTokenPayload


# Setup password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Token config
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
# Default to expire at 5h for user session
ACCESS_TOKEN_EXPIRE_MINUTES = 300
INVITE_TOKEN_EXPIRE_HOURS = 48
RESET_TOKEN_EXPIRE_HOURS = 2


# --- Password Hashing --- #
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT Token Handling --- #
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired token")


def create_reset_token(email: str) -> str:
    data = {
        "sub": email,
        "type": "reset"
    }
    return create_access_token(data, timedelta(hours=RESET_TOKEN_EXPIRE_HOURS))

def verify_reset_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            raise ValueError("Token payload missing 'sub'")
        return email  # email
    except JWTError:
        raise ValueError("Invalid or expired token")

def validate_token_type(token: str, expected_type: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != expected_type:
        raise ValueError("Invalid token type")
    return payload


# --- Current User --- #
def get_current_user(token: str = Depends(oauth2_scheme)) -> UserTokenPayload:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
        return UserTokenPayload(user_id=int(user_id), role=role)
    except JWTError:
        raise credentials_exception
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from . import models, schemas, utils
from .tasks import send_verification_email_task, send_password_reset_email_task, send_welcome_email_task


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, payload: schemas.UserRegister) -> models.User:
        """Register a new user"""
        # Check if user exists
        existing_user = self.db.query(models.User).filter(
            models.User.email == payload.email
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        verification_token = utils.generate_verification_token()
        hashed_password = utils.get_password_hash(payload.password)

        db_user = models.User(
            name=payload.name,
            email=payload.email,
            hashed_password=hashed_password,
            verification_token=verification_token,
            is_verified=False
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        # Send verification email asynchronously via Celery
        send_verification_email_task.delay(
            email=payload.email,
            name=payload.name,
            verification_token=verification_token
        )

        return db_user

    def login_user(self, payload: schemas.UserLogin) -> dict:
        """Login user and return JWT token"""
        user = self.db.query(models.User).filter(
            models.User.email == payload.email
        ).first()

        if not user or not utils.verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email before logging in"
            )

        access_token = utils.create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}

    def verify_email(self, token: str) -> models.User:
        """Verify user email with token"""
        user = self.db.query(models.User).filter(
            models.User.verification_token == token
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )

        user.is_verified = True
        user.verification_token = None
        self.db.commit()
        self.db.refresh(user)

        # Send welcome email asynchronously via Celery
        send_welcome_email_task.delay(
            email=user.email,
            name=user.name
        )

        return user

    def forgot_password(self, email: str) -> None:
        """Request password reset"""
        user: Optional[models.User] = self.db.query(models.User).filter(
            models.User.email == email
        ).first()

        if not user:
            # Don't reveal if email exists
            return

        reset_token = utils.generate_reset_token()
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)

        self.db.commit()

        # Send password reset email asynchronously via Celery
        send_password_reset_email_task.delay(
            email=email,
            name=user.name,
            reset_token=reset_token
        )

    def reset_password(self, token: str, new_password: str) -> models.User:
        """Reset password with token"""
        user = self.db.query(models.User).filter(
            models.User.reset_token == token
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

        if user.reset_token_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )

        user.hashed_password = utils.get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None

        self.db.commit()
        self.db.refresh(user)

        return user
from uuid import uuid4
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Boolean, Enum as SqlEnum
from app.db.base import Base
from sqlalchemy.sql import func

class APIClient(Base):
    __tablename__ = "api_clients"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, unique=True, nullable=False)
    api_key = Column(String, unique=True, nullable=False)  # Store **hashed**, not plain
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
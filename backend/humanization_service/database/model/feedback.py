from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from database.database_service import DatabaseService, Base

class Feedback(Base):
    """
    Represents feedback for different requests.
    """
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, nullable=False, index=True)
    feedback_score = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Auto timestamp

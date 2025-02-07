from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, func
from database.database_service import DatabaseService, Base

class HumanizationRequest(Base):
    """
    Stores details of humanization requests, tracking input, output, and transformation parameters.
    """
    __tablename__ = 'humanization_requests'

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(String, nullable=False)
    humanized_text = Column(String, nullable=True)  # Initially null until processed
    parameters = Column(JSON, nullable=False)  # Stores user-defined transformation parameters
    explanation_version_id = Column(Integer, ForeignKey("explanation_versions.id"), nullable=False, index=True)
    model_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Request creation timestamp
    processed_at = Column(DateTime(timezone=True), nullable=True)  # Set when humanization is complete

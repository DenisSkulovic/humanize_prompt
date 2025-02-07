from sqlalchemy import Column, Integer, String, DateTime, func, JSON
from database.database_service import DatabaseService, Base
from sqlalchemy import select

class ExplanationVersion(Base):
    """
    Represents explanation versions for different humanization scales.
    """
    __tablename__ = "explanation_versions"

    id = Column(Integer, primary_key=True, index=True)
    version_number = Column(Integer, nullable=False, index=True)
    scale_name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    examples = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

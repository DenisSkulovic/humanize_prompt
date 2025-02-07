from sqlalchemy import Column, Integer, String, DateTime, func, JSON
from database_service import Base

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

class ExplanationRepository:
    """
    Handles CRUD operations for explanation scales.
    """

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    async def create_explanation(self, version_number: float, scale_name: str, description: str, examples: str):
        """
        Creates a new explanation scale.
        """
        async with self.db_service.get_session() as session:
            explanation = ExplanationVersion(
                version_number=version_number,
                scale_name=scale_name,
                description=description,
                examples=examples
            )
            session.add(explanation)
            await session.commit()
            return explanation

    async def get_explanation(self, version_number: float, scale_name: str):
        """
        Retrieves a specific explanation scale by version and scale name.
        """
        async with self.db_service.get_session() as session:
            result = await session.execute(
                select(ExplanationVersion)
                .where(ExplanationVersion.version_number == version_number)
                .where(ExplanationVersion.scale_name == scale_name)
            )
            return result.scalars().first()

    async def list_explanations(self, version_number: float):
        """
        Lists all explanation scales for a given version.
        """
        async with self.db_service.get_session() as session:
            result = await session.execute(
                select(ExplanationVersion).where(ExplanationVersion.version_number == version_number)
            )
            return result.scalars().all()

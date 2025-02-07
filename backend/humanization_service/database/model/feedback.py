from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from backend.humanization_service.database.DatabaseService import DatabaseService, Base

class ExplanationVersion(Base):
    """
    Represents explanation versions for different humanization scales.
    """
    __tablename__ = "explanation_versions"

    id = Column(Integer, primary_key=True, index=True)
    version_number = Column(Integer, nullable=False, index=True)
    scale_name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    examples = Column(JSON, nullable=False)  # Stores example variations as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Auto timestamp

class ExplanationRepository:
    """
    Handles CRUD operations for explanation versions.
    """

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    async def create_explanation(self, version_number: float, scale_name: str, description: str, examples: dict) -> ExplanationVersion:
        """
        Creates a new explanation scale entry.
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
            await session.refresh(explanation)
            return explanation

    async def get_explanation(self, version_number: float, scale_name: str) -> ExplanationVersion | None:
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

    async def list_explanations(self, version_number: float) -> list[ExplanationVersion]:
        """
        Lists all explanation scales for a given version.
        """
        async with self.db_service.get_session() as session:
            result = await session.execute(
                select(ExplanationVersion).where(ExplanationVersion.version_number == version_number)
            )
            return result.scalars().all()

    async def update_explanation(self, version_number: float, scale_name: str, new_description: str, new_examples: dict) -> ExplanationVersion | None:
        """
        Updates an existing explanation entry.
        """
        async with self.db_service.get_session() as session:
            explanation = await session.execute(
                select(ExplanationVersion)
                .where(ExplanationVersion.version_number == version_number)
                .where(ExplanationVersion.scale_name == scale_name)
            )
            explanation = explanation.scalars().first()
            if explanation:
                explanation.description = new_description
                explanation.examples = new_examples
                await session.commit()
                await session.refresh(explanation)
            return explanation

    async def delete_explanation(self, version_number: float, scale_name: str) -> bool:
        """
        Deletes an explanation scale entry.
        """
        async with self.db_service.get_session() as session:
            explanation = await session.execute(
                select(ExplanationVersion)
                .where(ExplanationVersion.version_number == version_number)
                .where(ExplanationVersion.scale_name == scale_name)
            )
            explanation = explanation.scalars().first()
            if explanation:
                await session.delete(explanation)
                await session.commit()
                return True
        return False

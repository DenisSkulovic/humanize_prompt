from sqlalchemy import select
from database.database_service import DatabaseService
from database.model.explanation_version import ExplanationVersion

class ExplanationRepository:
    """
    Handles CRUD operations for explanation scales.
    """

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    async def create_explanation(self, version_number: int, scale_name: str, description: str, examples: str):
        """
        Creates a new explanation scale.
        """
        async for session in self.db_service.get_session():
            explanation = ExplanationVersion(
                version_number=version_number,
                scale_name=scale_name,
                description=description,
                examples=examples
            )
            session.add(explanation)
            await session.commit()
            return explanation

    async def get_explanation(self, scale_name: str, version_number: int = None):
        """
        Retrieves the latest explanation scale by version and scale name.
        If version_number is not provided, retrieves the latest explanation for the scale name.
        """
        async for session in self.db_service.get_session():
            query = select(ExplanationVersion).where(ExplanationVersion.scale_name == scale_name)
            if version_number is not None:
                query = query.where(ExplanationVersion.version_number == version_number)
            query = query.order_by(ExplanationVersion.id.desc()).limit(1)
            
            result = await session.execute(query)
            return result.scalars().first()
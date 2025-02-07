from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, func
from backend.humanization_service.database.DatabaseService import DatabaseService, Base

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

class HumanizationRepository:
    """
    Handles CRUD operations for humanization requests.
    """

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    async def create_request(self, original_text: str, parameters: dict, explanation_version_id: int, model_name: str) -> HumanizationRequest:
        """
        Creates a new humanization request.
        """
        async with self.db_service.get_session() as session:
            request = HumanizationRequest(
                original_text=original_text,
                parameters=parameters,
                explanation_version_id=explanation_version_id,
                model_name=model_name,
            )
            session.add(request)
            await session.commit()
            await session.refresh(request)
            return request

    async def update_request(self, request_id: int, humanized_text: str) -> HumanizationRequest | None:
        """
        Updates an existing request with the processed humanized text.
        """
        async with self.db_service.get_session() as session:
            request = await session.get(HumanizationRequest, request_id)
            if request:
                request.humanized_text = humanized_text
                request.processed_at = func.now()  # Mark processing completion
                await session.commit()
                await session.refresh(request)
            return request

    async def get_request(self, request_id: int) -> HumanizationRequest | None:
        """
        Retrieves a humanization request by ID.
        """
        async with self.db_service.get_session() as session:
            return await session.get(HumanizationRequest, request_id)

    async def delete_request(self, request_id: int) -> bool:
        """
        Deletes a humanization request by ID.
        """
        async with self.db_service.get_session() as session:
            request = await session.get(HumanizationRequest, request_id)
            if request:
                await session.delete(request)
                await session.commit()
                return True
        return False

    async def get_unprocessed_requests(self) -> list[HumanizationRequest]:
        """
        Retrieves all requests that haven't been processed yet.
        """
        async with self.db_service.get_session() as session:
            result = await session.execute(
                select(HumanizationRequest).where(HumanizationRequest.humanized_text == None)
            )
            return result.scalars().all()

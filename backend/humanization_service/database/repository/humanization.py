from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database_service import DatabaseService
from database.model.humanization import HumanizationRequest

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
        async for session in self.db_service.get_session():
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
        async for session in self.db_service.get_session():
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
        async for session in self.db_service.get_session():
            return await session.get(HumanizationRequest, request_id)

    async def delete_request(self, request_id: int) -> bool:
        """
        Deletes a humanization request by ID.
        """
        async for session in self.db_service.get_session():
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
        async for session in self.db_service.get_session():
            result = await session.execute(
                select(HumanizationRequest).where(HumanizationRequest.humanized_text == None)
            )
            return result.scalars().all()

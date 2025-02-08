from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database_service import DatabaseService
from database.model.humanization import HumanizationRequest
from typing import Dict

class HumanizationRepository:
    """
    Handles CRUD operations for humanization requests.
    """

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    async def create_request(
        self, 
        original_text: str, 
        parameters: dict, 
        explanation_versions: Dict[str, int] = None, 
        model_name: str = None
    ) -> HumanizationRequest:
        """
        Creates a new humanization request.
        """
        async for session in self.db_service.get_session():
            request = HumanizationRequest(
                original_text=original_text,
                parameters=parameters,
                explanation_versions=explanation_versions,
                model_name=model_name,
            )
            session.add(request)
            await session.commit()
            await session.refresh(request)
            return request

    async def update_request(
        self,
        request_id: int,
        original_text: str = None,
        parameters: dict = None,
        explanation_versions: Dict[str, int] = None,
        model_name: str = None,
        humanized_text: str = None
    ) -> HumanizationRequest | None:
        """
        Updates an existing request with the provided details and the processed humanized text.
        """
        async for session in self.db_service.get_session():
            request = await session.get(HumanizationRequest, request_id)
            if request:
                if original_text is not None:
                    request.original_text = original_text
                if parameters is not None:
                    request.parameters = parameters
                if explanation_versions is not None:
                    request.explanation_versions = explanation_versions
                if model_name is not None:
                    request.model_name = model_name
                if humanized_text is not None:
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
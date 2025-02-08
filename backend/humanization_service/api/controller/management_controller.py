from fastapi import APIRouter, Depends, HTTPException
from services.explanation_service import ExplanationService
from database.database_service import DatabaseService
from dto.explanation_dto import ExplanationDTO
from typing import List

class ManagementController:
    """
    Handles management of explanation versions and scale settings.
    """

    def __init__(self, db_service: DatabaseService):
        self.router = APIRouter(prefix="/management", tags=["Management"])
        self.db_service = db_service
        self.explanation_service = ExplanationService(db_service)

        # Register endpoints
        self.router.post("/explanations")(self.create_explanation_version)

    async def create_explanation_version(self, explanation: ExplanationDTO):
        """
        Creates a new explanation version.
        """
        result = await self.explanation_service.create_explanation(
            version_number=explanation.version_number,
            scale_name=explanation.scale_name,
            description=explanation.description,
            examples=explanation.examples
        )
        return {"message": "Explanation version created", "version_id": result.id}

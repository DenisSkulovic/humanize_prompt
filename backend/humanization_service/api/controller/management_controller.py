from fastapi import APIRouter, Depends, HTTPException
from backend.humanization_service.services.explanation_service import ExplanationService
from backend.humanization_service.database.DatabaseService import DatabaseService
from backend.humanization_service.dto.explanation_dto import ExplanationDTO
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
        self.router.get("/explanations/{version_id}")(self.get_explanation_version)
        self.router.get("/explanations")(self.list_explanation_versions)
        self.router.delete("/explanations/{version_id}")(self.delete_explanation_version)

    async def create_explanation_version(self, explanation: ExplanationDTO):
        """
        Creates a new explanation version.
        """
        result = await self.explanation_service.create_explanation(
            explanation.text, explanation.version_number
        )
        return {"message": "Explanation version created", "version_id": result.id}

    async def get_explanation_version(self, version_id: int):
        """
        Retrieves a specific explanation version by ID.
        """
        explanation = await self.explanation_service.get_explanation(version_id)
        if not explanation:
            raise HTTPException(status_code=404, detail="Explanation version not found")
        return explanation

    async def list_explanation_versions(self) -> List[ExplanationDTO]:
        """
        Lists all explanation versions.
        """
        return await self.explanation_service.list_explanations()

    async def delete_explanation_version(self, version_id: int):
        """
        Deletes an explanation version.
        """
        deleted = await self.explanation_service.delete_explanation(version_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Explanation version not found or already deleted")
        return {"message": "Explanation version deleted"}

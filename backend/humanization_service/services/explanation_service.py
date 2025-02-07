import json
from database.repository.explanation_version import ExplanationRepository
from dto.explanation_dto import ExplanationDTO

class ExplanationService:
    """
    Handles operations related to explanation versions.
    """

    def __init__(self, db_service):
        self.db_service = db_service
        self.explanation_repository = ExplanationRepository(db_service)

    async def create_explanation(self, text: str, version_number: int) -> ExplanationDTO:
        """
        Creates a new explanation version.
        """
        explanation = await self.explanation_repository.create_explanation(
            version_number=version_number,
            scale_name="default_scale",  # Assuming a default scale name for simplicity
            description=text,
            examples="default_examples"  # Assuming default examples for simplicity
        )
        return ExplanationDTO(
            id=explanation.id,
            text=explanation.description,
            version_number=explanation.version_number
        )

    async def get_explanation(self, scale_name: str, version_number: int = None) -> ExplanationDTO:
        """
        Retrieves the latest explanation version by scale name and version number.
        """
        explanation = await self.explanation_repository.get_explanation(scale_name, version_number)
        if explanation:
            return ExplanationDTO(
                id=explanation.id,
                text=explanation.description,
                version_number=explanation.version_number
            )
        return None


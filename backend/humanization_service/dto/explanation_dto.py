from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime

class ExplanationDTO(BaseModel):
    """
    DTO for explanation version management.
    """
    version_number: int = Field(..., description="Version number of the explanation settings")
    scale_name: str = Field(..., description="Name of the humanization scale")
    description: str = Field(..., description="Description of the humanization scale")
    examples: Dict[str, Any] = Field(..., description="Examples for the humanization scale")

    @staticmethod
    def build(version_number: int, scale_name: str, description: str, examples: Dict[str, Any], created_at: datetime):
        return ExplanationDTO(
            version_number=version_number,
            scale_name=scale_name,
            description=description,
            examples=examples,
        )

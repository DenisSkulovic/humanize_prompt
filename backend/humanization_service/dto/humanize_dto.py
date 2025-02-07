from pydantic import BaseModel, Field
from typing import Dict, Optional

class HumanizationRequestDTO(BaseModel):
    """
    DTO for humanization requests.
    """
    original_text: str = Field(..., min_length=1, description="Text to be humanized")
    parameters: Dict[str, int] = Field(..., description="Settings for humanization (e.g., casualness, humor)")
    explanation_version_id: Optional[int] = Field(None, description="Version of the explanation rules to apply (Defaults to latest)")

    @staticmethod
    def build(original_text: str, parameters: Dict[str, int], explanation_version_id: Optional[int] = None):
        return HumanizationRequestDTO(
            original_text=original_text,
            parameters=parameters,
            explanation_version_id=explanation_version_id
        )

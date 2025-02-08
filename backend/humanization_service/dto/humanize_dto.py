from pydantic import BaseModel, Field
from typing import Dict, Optional

class HumanizationRequestDTO(BaseModel):
    """
    DTO for humanization requests.
    """
    request_id: int = Field(..., description="Unique identifier for the request")
    original_text: str = Field(..., min_length=1, description="Text to be humanized")
    parameters: Dict[str, int] = Field(..., description="Settings for humanization (e.g., casualness, humor)")
    parameter_explanation_versions: Optional[Dict[str, str]] = Field(None, description="Explanation versions for each parameter")
    model_name: str = Field(..., description="Name of the OpenAI model to use")

    @staticmethod
    def build(request_id: int, original_text: str, parameters: Dict[str, int], model_name: str, parameter_explanation_versions: Optional[Dict[str, str]] = None):
        return HumanizationRequestDTO(
            request_id=request_id,
            original_text=original_text,
            parameters=parameters,
            parameter_explanation_versions=parameter_explanation_versions,
            model_name=model_name
        )
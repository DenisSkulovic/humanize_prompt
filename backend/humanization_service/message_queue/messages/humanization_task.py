from pydantic import BaseModel
from typing import Dict

class HumanizationTask(BaseModel):
    """
    Represents a humanization task to be processed asynchronously.
    """
    request_id: int
    original_text: str
    model_name: str
    parameters: Dict[str, int]
    parameter_explanation_versions: Dict[str, str]
    queue_name: str  # Where the result should be sent back

    @staticmethod
    def build(request_id: int, original_text: str, model_name: str, parameters: Dict[str, int], parameter_explanation_versions: Dict[str, str], queue_name: str):
        return HumanizationTask(
            request_id=request_id,
            original_text=original_text,
            model_name=model_name,
            parameters=parameters,
            parameter_explanation_versions=parameter_explanation_versions,
            queue_name=queue_name
        )

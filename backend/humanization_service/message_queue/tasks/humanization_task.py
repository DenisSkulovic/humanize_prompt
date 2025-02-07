from pydantic import BaseModel
from typing import Dict

class HumanizationTask(BaseModel):
    """
    Represents a humanization task to be processed asynchronously.
    """
    request_id: int
    original_text: str
    parameters: Dict[str, int]
    explanation_texts: Dict[str, str]  # Explanation scale text mappings
    queue_name: str  # Where the result should be sent back

    @staticmethod
    def build(request_id: int, original_text: str, model_name: str, parameters: Dict[str, int], explanation_texts: Dict[str, str], queue_name: str):
        return HumanizationTask(
            request_id=request_id,
            original_text=original_text,
            model_name=model_name,
            parameters=parameters,
            explanation_texts=explanation_texts,
            queue_name=queue_name
        )

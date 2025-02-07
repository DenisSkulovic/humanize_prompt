from pydantic import BaseModel, Field

class FeedbackDTO(BaseModel):
    """
    DTO for feedback submission.
    """
    humanization_request_id: int = Field(..., description="ID of the humanization request being reviewed")
    feedback_score: int = Field(..., ge=-2, le=2, description="User rating (-2: AI-like, 2: Human-like)")

    @staticmethod
    def build(humanization_request_id: int, feedback_score: int):
        return FeedbackDTO(humanization_request_id=humanization_request_id, feedback_score=feedback_score)

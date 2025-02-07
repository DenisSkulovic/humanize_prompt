from database.repository.feedback import FeedbackRepository
from dto.feedback_dto import FeedbackDTO

class FeedbackService:
    """
    Handles feedback-related operations such as creating feedback and retrieving feedback statistics.
    """

    def __init__(self, db_service):
        self.db_service = db_service
        self.feedback_repository = FeedbackRepository(db_service)

    async def create_feedback(self, humanization_request_id: int, feedback_score: int) -> FeedbackDTO:
        """
        Creates a new feedback entry for a humanization request.
        """
        feedback = await self.feedback_repository.create_feedback(humanization_request_id, feedback_score)
        return FeedbackDTO(
            id=feedback.id,
            humanization_request_id=feedback.humanization_request_id,
            feedback_score=feedback.feedback_score,
            created_at=feedback.created_at
        )
from fastapi import APIRouter, Depends, HTTPException
from services.feedback_service import FeedbackService
from database.database_service import DatabaseService
from dto.feedback_dto import FeedbackDTO
from typing import List

class FeedbackController:
    """
    Handles user feedback submission and retrieval.
    """

    def __init__(self, db_service: DatabaseService):
        self.router = APIRouter(prefix="/feedback", tags=["Feedback"])
        self.db_service = db_service
        self.feedback_service = FeedbackService(db_service)

        # Register endpoints
        self.router.post("/")(self.submit_feedback)

    async def submit_feedback(self, feedback: FeedbackDTO):
        """
        Submits feedback for a humanization request.
        """
        result = await self.feedback_service.create_feedback(feedback.humanization_request_id, feedback.feedback_score)
        return {"message": "Feedback submitted successfully", "feedback_id": result.id}

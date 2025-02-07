from fastapi import APIRouter, Depends, HTTPException
from backend.humanization_service.services.feedback_service import FeedbackService
from backend.humanization_service.database.DatabaseService import DatabaseService
from backend.humanization_service.dto.feedback_dto import FeedbackDTO
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
        self.router.get("/{request_id}")(self.get_feedback_by_request)
        self.router.get("/stats/{request_id}")(self.get_feedback_stats)

    async def submit_feedback(self, feedback: FeedbackDTO):
        """
        Submits feedback for a humanization request.
        """
        result = await self.feedback_service.create_feedback(feedback.humanization_request_id, feedback.feedback_score)
        return {"message": "Feedback submitted successfully", "feedback_id": result.id}

    async def get_feedback_by_request(self, request_id: int) -> List[FeedbackDTO]:
        """
        Retrieves all feedback entries for a given humanization request.
        """
        feedback_entries = await self.feedback_service.get_feedback_by_request(request_id)
        if not feedback_entries:
            raise HTTPException(status_code=404, detail="No feedback found for this request")
        return feedback_entries

    async def get_feedback_stats(self, request_id: int):
        """
        Retrieves aggregated feedback stats for a given humanization request.
        Example: Average score for a request.
        """
        avg_score = await self.feedback_service.get_average_feedback_score(request_id)
        return {"request_id": request_id, "average_feedback_score": avg_score}



from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database_service import DatabaseService
from database.model.feedback import Feedback

class FeedbackRepository:
    """
    Handles CRUD operations for feedback entries.
    """

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    async def create_feedback(self, request_id: int, feedback_score: int) -> Feedback:
        """
        Creates a new feedback entry.
        """
        async for session in self.db_service.get_session():
            feedback = Feedback(
                request_id=request_id,
                feedback_score=feedback_score
            )
            session.add(feedback)
            await session.commit()
            await session.refresh(feedback)
            return feedback
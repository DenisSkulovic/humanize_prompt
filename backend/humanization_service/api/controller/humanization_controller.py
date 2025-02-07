from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from services.humanization_service import HumanizationService
from message_queue.message_queue_service import MessageQueueService
from database.database_service import DatabaseService
from dto.humanize_dto import HumanizationRequestDTO
from cache.cache_service import CacheService
import asyncio
import json

class HumanizationController:
    """
    Controller for handling humanization requests using WebSocket streaming.
    """

    def __init__(self, db_service: DatabaseService, cache_service: CacheService, messaging_service: MessageQueueService):
        self.router = APIRouter(prefix="/humanize", tags=["Humanization"])
        self.db_service = db_service
        self.cache_service = cache_service
        self.messaging_service = messaging_service
        self.humanization_service = HumanizationService(db_service, cache_service, messaging_service)

        # Register WebSocket endpoint
        self.router.websocket("/ws")(self.websocket_humanization)

    async def websocket_humanization(self, websocket: WebSocket):
        """
        Handles real-time humanization through WebSocket communication.
        """
        await websocket.accept()
        connection_id = str(websocket.client)  # Simple identifier for tracking

        try:
            while True:
                # Receive input text and parameters from the client
                data = await websocket.receive_text()
                request = HumanizationRequestDTO.parse_raw(data)

                # Build the task
                task = HumanizationTask.build(request.id, request.original_text, request.model_name, request.parameters, request.parameter_explanation_versions, request.queue_name)

                # Publish task to RabbitMQ
                task_id = await self.messaging_service.publish("humanization_task", task.dict())

                # Subscribe to the response queue
                async for chunk in self.messaging_service.consume(f"humanization_result_{task_id}"):
                    await websocket.send_text(chunk)  # Stream chunks to the client

                await websocket.close()
                break

        except WebSocketDisconnect:
            print(f"WebSocket disconnected: {connection_id}")

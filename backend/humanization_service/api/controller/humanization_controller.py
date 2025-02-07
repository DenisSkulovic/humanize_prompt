from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from backend.humanization_service.services.humanization_service import HumanizationService
from backend.humanization_service.services.message_queue_service import MessageQueueService
from backend.humanization_service.database.DatabaseService import DatabaseService
from backend.humanization_service.dto.humanize_dto import HumanizationRequestDTO
import asyncio
import json

class HumanizationController:
    """
    Controller for handling humanization requests using WebSocket streaming.
    """

    def __init__(self, db_service: DatabaseService, messaging_service: MessageQueueService):
        self.router = APIRouter(prefix="/humanize", tags=["Humanization"])
        self.db_service = db_service
        self.messaging_service = messaging_service
        self.humanization_service = HumanizationService(db_service)

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

                # Publish task to RabbitMQ (or another queue)
                task_id = await self.messaging_service.publish("humanization_task", request.dict())

                # Subscribe to the response queue
                async for chunk in self.messaging_service.consume(f"humanization_result_{task_id}"):
                    await websocket.send_text(chunk)  # Stream chunks to the client

                # Store the final response in the database
                final_result = "".join(await self.messaging_service.collect_results(f"humanization_result_{task_id}"))
                await self.humanization_service.store_humanization(request, final_result) # TODO include other necessary things, this is a shallow draft

                await websocket.close()
                break

        except WebSocketDisconnect:
            print(f"WebSocket disconnected: {connection_id}")

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from services.humanization_service import HumanizationService
from message_queue.message_queue_service import MessageQueueService
from database.database_service import DatabaseService
from dto.humanize_dto import HumanizationRequestDTO
from cache.cache_service import CacheService
from message_queue.messages.humanization_task import HumanizationTask
import asyncio
import json
from core.config import Config
from message_queue.messages.humanized_queue_message import HumanizedQueueMessage

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
                print(f"Received request: {request}", flush=True)
                # Build the task
                task = HumanizationTask.build(
                    request_id=request.request_id,
                    original_text=request.original_text,
                    model_name=request.model_name,
                    parameters=request.parameters,
                    parameter_explanation_versions=request.parameter_explanation_versions,
                    queue_name="humanization_task"
                )

                # Publish task to RabbitMQ
                task_id = await self.messaging_service.publish(queue_name="humanization_task", message=json.dumps(task.dict()))

                # Subscribe to the response queue
                queue_name = f"humanization_result_{request.request_id}"
                print("queue_name", queue_name, flush=True)
                isLast = False
                async for chunk in self.messaging_service.consume(queue_name=queue_name):
                    print("1")
                    parsed_chumk = json.loads(chunk)
                    print("2")
                    message = HumanizedQueueMessage(isLast=parsed_chumk["isLast"], text_piece=parsed_chumk["text_piece"], final_text=parsed_chumk["final_text"])
                    print("3")
                    isLast = message.isLast
                    print("4")
                    await websocket.send_text(json.dumps(message.to_dict()))  # Stream chunks to the client
                    print("5")
                    if isLast:
                        break

                await websocket.close()
                break

        except WebSocketDisconnect:
            print(f"WebSocket disconnected: {connection_id}")

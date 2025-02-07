import json
import asyncio
from backend.humanization_service.repositories.humanization_repository import HumanizationRepository
from backend.humanization_service.services.cache_service import CacheService
from backend.humanization_service.services.message_queue_service import MessageQueueService
from backend.humanization_service.dto.humanize_dto import HumanizationRequestDTO
from backend.humanization_service.models.humanization_task import HumanizationTask
from backend.humanization_service.repositories.explanation_repository import ExplanationRepository

class HumanizationService:
    """
    Handles text humanization by fetching explanation data, queuing the task,
    streaming responses via WebSocket, and storing results in the database.
    """


    def __init__(self, db_service, cache_service: CacheService, messaging_service: MessageQueueService):
        self.db_service = db_service
        self.cache_service = cache_service
        self.messaging_service = messaging_service
        self.humanization_repository = HumanizationRepository(db_service)
        self.explanation_repository = ExplanationRepository(db_service)


    async def build_prompt(self, original_text: str, parameters: dict, explanation_texts: dict) -> str:
        """
        Constructs the system prompt for OpenAI based on parameters and explanations.
        """
        prompt_lines = [
            "You are transforming text to be more human-like based on the following parameters:",
        ]

        for scale, value in parameters.items():
            explanation = explanation_texts.get(scale, "No explanation available.")
            prompt_lines.append(f"- {scale.capitalize()}: {value}/10 → {explanation}")

        prompt_lines.append(f"\nUser input: \"{original_text}\"")
        prompt_lines.append("Generate the humanized response.")

        return "\n".join(prompt_lines)


    async def get_explanation_texts(self, version_id: int) -> dict:
        """
        Retrieves explanation texts from cache (Redis) or the database.
        """
        cache_key = f"explanation_version_{version_id}"
        cached_explanations = await self.cache_service.get(cache_key)

        if cached_explanations:
            return json.loads(cached_explanations)  # Load from cache

        # Fetch from DB if not cached
        explanations = await self.explanation_repository.list_explanations(version_id)
        if not explanations:
            raise ValueError(f"Explanation version {version_id} not found.")

        # Transform into {scale_name: explanation_text}
        explanation_texts = {exp.scale_name: exp.description for exp in explanations}

        # Cache in Redis
        await self.cache_service.set(cache_key, json.dumps(explanation_texts))

        return explanation_texts


    async def store_humanized_text(self, request_id: int, humanized_text: str):
        """
        Stores the final humanized text in the database after processing.
        """
        await self.humanization_repository.update_request(request_id, humanized_text)


    async def process_humanization(self, request: HumanizationRequestDTO, websocket):
        """
        Processes a humanization request via WebSocket, streaming results in real-time.
        """
        # Determine explanation version
        if request.explanation_version_id is None:
            latest_version = await self.explanation_repository.get_latest_version()
            request.explanation_version_id = latest_version

        # Fetch explanations
        explanation_texts = await self.get_explanation_texts(request.explanation_version_id)

        # Store request in DB
        created_request = await self.humanization_repository.create_request(
            request.original_text, request.parameters, request.explanation_version_id
        )

        # Prepare RabbitMQ task
        task = HumanizationTask.build(
            request_id=created_request.id,
            original_text=request.original_text,
            parameters=request.parameters,
            explanation_texts=explanation_texts,
            queue_name=f"humanization_result_{created_request.id}"
        )

        # Publish task
        await self.messaging_service.publish("humanization_task", task.dict())

        # Stream results via WebSocket
        collected_chunks = []
        async for chunk in self.messaging_service.consume(f"humanization_result_{created_request.id}"):
            await websocket.send_text(chunk)  # Stream chunk
            collected_chunks.append(chunk)

        # Concatenate full response
        final_text = "".join(collected_chunks)

        # Store result in DB
        await self.humanization_repository.update_request(created_request.id, final_text)

        # Close connection
        await websocket.close()

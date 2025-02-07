import json
import asyncio
from database.repository.humanization import HumanizationRepository
from cache.cache_service import CacheService
from message_queue.message_queue_service import MessageQueueService
from dto.humanize_dto import HumanizationRequestDTO
from message_queue.tasks.humanization_task import HumanizationTask
from database.repository.explanation_version import ExplanationRepository
from typing import Dict

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


    async def get_explanation_texts(self, parameters: Dict[str, any], parameter_explanation_versions: Dict[str, str]) -> dict:
        """
        Retrieves explanation texts from cache (Redis) or the database.
        """
        explanation_texts = {}

        for scale_name in parameters.keys():
            version = parameter_explanation_versions.get(scale_name, "LATEST")
            cache_key = f"explanation_version_{version}_{scale_name}"

            cached_explanation = await self.cache_service.get(cache_key)
            if cached_explanation:
                explanation_texts[scale_name] = json.loads(cached_explanation)
                continue

            # Fetch from DB if not cached
            explanation = await self.explanation_repository.get_explanation(scale_name, version_number=version if version != "LATEST" else None)
            if not explanation:
                raise ValueError(f"Explanation version {version} not found for scale {scale_name}.")

            # Transform into {scale_name: explanation_text}
            explanation_texts[scale_name] = explanation

            # Cache in Redis (under specific version name, and also under LATEST if no specific varions was provided and LATEST was used)
            await self.cache_service.set(cache_key, json.dumps(explanation))
            if version == "LATEST":
                latest_cache_key = f"explanation_version_LATEST_{scale_name}"
                await self.cache_service.set(latest_cache_key, json.dumps(explanation))

        return explanation_texts


    async def store_humanized_text(self, request_id: int, humanized_text: str):
        """
        Stores the final humanized text in the database after processing.
        """
        await self.humanization_repository.update_request(request_id, humanized_text)
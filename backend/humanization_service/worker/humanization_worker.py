import asyncio
import json
from backend.humanization_service.services.humanization_service import HumanizationService
from backend.humanization_service.services.message_queue_service import MessageQueueService
from backend.humanization_service.database.DatabaseService import DatabaseService
from backend.humanization_service.dto.humanize_dto import HumanizationTask
from backend.humanization_service.services.cache_service import CacheService
from openai import AsyncOpenAI  # Assuming OpenAI async SDK is used

class HumanizationWorker:
    """
    Worker for processing humanization tasks from RabbitMQ.
    """

    def __init__(self):
        self.db_service = DatabaseService()
        self.cache_service = CacheService()
        self.messaging_service = MessageQueueService()
        self.humanization_service = HumanizationService(self.db_service, self.cache_service, self.messaging_service)
        self.openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

    async def process_task(self, task: HumanizationTask):
        """
        Processes a single humanization task.
        """
        model_name = task.model_name
        for attempt in range(3):  # Retry up to 3 times
            try:
                # Step 1: Construct system prompt from explanations and parameters
                system_prompt = await self.humanization_service.build_prompt(
                    task.original_text, task.parameters, task.explanation_texts
                )

                # Step 2: Call OpenAI API
                async with self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "system", "content": system_prompt}],
                    stream=True
                ) as response:
                    collected_chunks = []

                    async for chunk in response:
                        chunk_text = chunk.choices[0].delta.get("content", "")
                        collected_chunks.append(chunk_text)

                        # Step 3: Stream chunk back to RabbitMQ result queue
                        await self.messaging_service.publish(task.queue_name, chunk_text)

                # Step 4: Concatenate the final response and store in DB
                final_text = "".join(collected_chunks)
                await self.humanization_service.store_humanized_text(task.request_id, final_text)
                break  # Exit loop if successful

            except Exception as e:
                print(f"Retrying task {task.request_id}, attempt {attempt+1}...", flush=True)
                await asyncio.sleep(2)


    async def run_worker(self):
        """
        Continuously listens to the RabbitMQ queue for humanization tasks.
        """
        print("[Worker] Listening for humanization tasks...")
        async for task_json in self.messaging_service.consume("humanization_task"):
            task_data = json.loads(task_json)
            task = HumanizationTask(**task_data)
            await self.process_task(task)

if __name__ == "__main__":
    worker = HumanizationWorker()
    asyncio.run(worker.run_worker())

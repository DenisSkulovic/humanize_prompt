import asyncio
import json
import psutil  # System resource monitoring
from services.humanization_service import HumanizationService
from message_queue.message_queue_service import MessageQueueService
from database.database_service import DatabaseService
from message_queue.messages.humanization_task import HumanizationTask
from message_queue.messages.humanized_queue_message import HumanizedQueueMessage
from cache.cache_service import CacheService
from openai import AsyncOpenAI
from core.config import Config

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
        self.current_concurrency = Config.MIN_CONCURRENT_TASKS
        self.semaphore = asyncio.Semaphore(self.current_concurrency)

    async def process_task(self, task: HumanizationTask):
        """Processes a single humanization task."""
        try:
            print(f"[Worker] Processing task {task.request_id}", flush=True)
            explanation_texts = await self.humanization_service.get_explanation_texts(
                parameters=task.parameters, parameter_explanation_versions=task.parameter_explanation_versions
            )

            system_prompt = await self.humanization_service.build_prompt(
                task.original_text, task.parameters, explanation_texts
            )

            response = await self.openai_client.chat.completions.create(
                model=task.model_name,
                messages=[{"role": "system", "content": system_prompt}],
                stream=True
            )

            queue_name = f"humanization_result_{task.request_id}"
            collected_chunks = []
            async for chunk in response:
                chunk_text = getattr(chunk.choices[0].delta, "content", None)
                if chunk_text:
                    collected_chunks.append(chunk_text)
                    await self.messaging_service.send_message(queue_name=queue_name, message=json.dumps({
                        "isLast": False,
                        "text_piece": chunk_text,
                        "final_text": ""
                    }))

            final_text = "".join(collected_chunks)
            await self.messaging_service.send_message(queue_name=queue_name, message=json.dumps({
                "isLast": True,
                "text_piece": "",
                "final_text": final_text
            }))

            await self.humanization_service.store_humanized_text(
                task=task, humanized_text=final_text,
                explanation_versions={scale: explanation["version_number"] for scale, explanation in explanation_texts.items()}
            )

            print(f"[Worker] Task {task.request_id} completed", flush=True)

        except Exception as e:
            print(f"❌ Error processing task {task.request_id}: {e}", flush=True)

    async def get_queue_size(self):
        """Simulate checking RabbitMQ queue size (replace with real implementation)."""
        return await self.messaging_service.get_queue_length("humanization_task")

    async def adjust_concurrency(self):
        """Dynamically adjusts concurrency based on system load and queue size."""
        while True:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            queue_size = await self.get_queue_size()

            if cpu_usage < 50 and memory_usage < 50 and queue_size > Config.INCREASE_CONCURRENCY_TASK_THRESHOLD:
                self.current_concurrency = min(self.current_concurrency + 1, Config.MAX_CONCURRENT_TASKS)
            elif cpu_usage > 80 or memory_usage > 80 or queue_size < Config.DECREASE_CONCURRENCY_TASK_THRESHOLD:
                self.current_concurrency = max(self.current_concurrency - 1, Config.MIN_CONCURRENT_TASKS)

            self.semaphore = asyncio.Semaphore(self.current_concurrency)
            print(f"[Worker] Adjusted concurrency to {self.current_concurrency} (CPU: {cpu_usage}%, Mem: {memory_usage}%, Queue: {queue_size})", flush=True)

            await asyncio.sleep(Config.ADJUST_CONCURRENCY_INTERVAL)

    async def run_worker(self):
        """Continuously listens to RabbitMQ and processes tasks dynamically."""
        print("[Worker] Listening for humanization tasks...", flush=True)

        asyncio.create_task(self.adjust_concurrency())

        tasks = set()

        async for task_json in self.messaging_service.get_next_message("humanization_task"):
            task_data = json.loads(task_json)
            task = HumanizationTask(**task_data)

            async def process_with_semaphore():
                async with self.semaphore:
                    await self.process_task(task)
                    tasks.discard(asyncio.current_task())

            new_task = asyncio.create_task(process_with_semaphore())
            tasks.add(new_task)

            tasks = {t for t in tasks if not t.done()}

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    worker = HumanizationWorker()
    asyncio.run(worker.run_worker())

import asyncio
import json
from services.humanization_service import HumanizationService
from message_queue.message_queue_service import MessageQueueService
from database.database_service import DatabaseService
from message_queue.messages.humanization_task import HumanizationTask
from message_queue.messages.humanized_queue_message import HumanizedQueueMessage
from cache.cache_service import CacheService
from openai import AsyncOpenAI
from core.config import Config

attempts = 1

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
        print("[Worker] model_name", model_name, flush=True)
        for attempt in range(attempts if attempts else 3):
            try:
                explanation_texts = await self.humanization_service.get_explanation_texts(parameters=task.parameters, parameter_explanation_versions=task.parameter_explanation_versions)
                print("[Worker] explanation_texts", explanation_texts, flush=True)

                # Step 1: Construct system prompt from explanations and parameters
                system_prompt = await self.humanization_service.build_prompt(
                    task.original_text, task.parameters, explanation_texts
                )
                print("[Worker] system_prompt", system_prompt, flush=True)

                # Step 2: Call OpenAI API
                # TODO: I was debugging this part and carelessly made it await the response. This is not correct. This way it basically waits for all the chunks, and only then streams them instantly. It instead should stream the chunks as they come in.
                response = await self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "system", "content": system_prompt}],
                    stream=True
                )

                collected_chunks = []
                async for chunk in response:
                    
                    chunk_text = getattr(chunk.choices[0].delta, "content", None)
                    print("[Worker] chunk_text", chunk_text, flush=True)
                    
                    if chunk_text:  # Only process non-empty chunks
                        collected_chunks.append(chunk_text)

                        # Step 3: Stream chunk back to RabbitMQ result queue
                        queue_name = f"humanization_result_{task.request_id}"
                        print("[Worker] queue_name", queue_name, flush=True)
                        message = HumanizedQueueMessage(isLast=False, text_piece=chunk_text)
                        print("[Worker] message", message, flush=True)
                        await self.messaging_service.publish(queue_name=queue_name, message=json.dumps(message.to_dict()))

                # Step 4: Concatenate the final response and store in DB
                final_text = "".join(collected_chunks)
                print("[Worker] final_text", final_text, flush=True)

                final_message = HumanizedQueueMessage(isLast=True, final_text=final_text)
                await self.messaging_service.publish(queue_name=queue_name, message=json.dumps(final_message.to_dict()))
                
                explanation_versions = {scale: explanation["version_number"] for scale, explanation in explanation_texts.items()}
                print("[Worker] explanation_versions", explanation_versions, flush=True)
                await self.humanization_service.store_humanized_text(
                    task = task,
                    humanized_text = final_text,
                    explanation_versions = explanation_versions
                )
                break  # Exit loop if successful

            except Exception as e:
                print(f"Error processing task {task.request_id}: {e}", flush=True)
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

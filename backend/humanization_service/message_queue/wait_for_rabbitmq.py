import asyncio
from aio_pika import connect_robust
from core.config import Config

async def wait_for_rabbitmq(sleep_interval=2):
    """Waits for RabbitMQ to be available before starting services."""
    print("[entrypoint.py] Waiting for RabbitMQ...", flush=True)
    attempts = 0
    total_wait_time = 0
    while True:
        attempts += 1
        print(f"[entrypoint.py] Attempting to connect to RabbitMQ... (Attempt {attempts}, Total wait time: {total_wait_time}s)", flush=True)
        try:
            connection = await connect_robust(Config.RABBITMQ_URL)
            await connection.close()
            print("[entrypoint.py] RabbitMQ is ready.", flush=True)
            break
        except Exception as e:
            print(f"[entrypoint.py] Waiting for RabbitMQ... ({e})", flush=True)
            await asyncio.sleep(sleep_interval)
            total_wait_time += sleep_interval

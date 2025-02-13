import subprocess
import time
import os
import asyncio
from aio_pika import connect_robust
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.config import Config
import asyncpg
from database.wait_for_postgres import wait_for_postgres
from message_queue.wait_for_rabbitmq import wait_for_rabbitmq

role_to_command = {
    "api": ["python3", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"],
    "worker": ["python3", "-m", "worker.humanization_worker"]
}

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, process_cmd):
        self.process_cmd = process_cmd
        self.process = None
        self.start_process()

    def start_process(self):
        print(f"[entrypoint.py ReloadHandler start_process] Starting process", flush=True)
        if self.process:
            print(f"[entrypoint.py ReloadHandler start_process] Terminating existing process", flush=True)
            self.process.terminate()
        print(f"[entrypoint.py ReloadHandler start_process] Starting new process", flush=True)
        self.process = subprocess.Popen(self.process_cmd)

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"[entrypoint.py ReloadHandler on_modified] File changed: {event.src_path}. Restarting process...", flush=True)
            self.start_process()

def main():
    """Main entrypoint for API & Worker based on ROLE."""
    print(f"[entrypoint.py] Role: {Config.ROLE}", flush=True)
    if Config.OPENAI_API_KEY:
        print(f"[entrypoint.py] OpenAI API Key length: {len(Config.OPENAI_API_KEY)}", flush=True)
    else:
        print("[entrypoint.py] OpenAI API Key is not defined", flush=True)
    print(f"[entrypoint.py] Redis URL: {Config.REDIS_URL}", flush=True)
    print(f"[entrypoint.py] Redis TTL: {Config.REDIS_TTL}", flush=True)
    print(f"[entrypoint.py] RabbitMQ URL: {Config.RABBITMQ_URL}", flush=True)
    print(f"[entrypoint.py] PostgreSQL URL: {Config.DATABASE_URL}", flush=True)
    print(f"[entrypoint.py] PostgreSQL URL Async PG: {Config.DATABASE_URL_ASYNC_PG}", flush=True)

    if Config.ROLE not in role_to_command:
        raise ValueError(f"[entrypoint.py] Unsupported role: {Config.ROLE}")

    # Wait for RabbitMQ and PostgreSQL
    async def wait_for_services():
        await asyncio.gather(
            wait_for_rabbitmq(),
            wait_for_postgres()
        )
    asyncio.run(wait_for_services())

    # Start process with auto-reload
    print(f"[entrypoint.py] Starting {Config.ROLE} with auto-reload...", flush=True)
    handler = ReloadHandler(role_to_command[Config.ROLE])
    observer = Observer()
    observer.schedule(handler, path=".", recursive=True)
    observer.start()

    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()

    handler.process.terminate()

if __name__ == "__main__":
    main()

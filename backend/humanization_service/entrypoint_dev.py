import subprocess
import time
import os
import asyncio
from aio_pika import connect_robust
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from database.run_alembic_migrations import run_alembic_migrations
from database.generate_migrations import generate_migration_if_schema_changed
from database.initialize_db import initialize_db
from core.config import Config

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

async def wait_for_postgres():
    """Wait for PostgreSQL to be ready before starting the API."""
    print("[entrypoint.py] Waiting for PostgreSQL...", flush=True)
    retries = 10
    while retries > 0:
        try:
            conn = await asyncpg.connect(Config.DATABASE_URL)
            await conn.close()
            print("[entrypoint.py] PostgreSQL is ready!", flush=True)
            return
        except Exception as e:
            print(f"[entrypoint.py] PostgreSQL not ready: {e}", flush=True)
            time.sleep(2)
            retries -= 1
    raise RuntimeError("PostgreSQL did not become ready in time.")

async def wait_for_rabbitmq():
    """Waits for RabbitMQ to be available before starting services."""
    print("[entrypoint.py] Waiting for RabbitMQ...", flush=True)
    while True:
        try:
            connection = await connect_robust(Config.RABBITMQ_URL)
            await connection.close()
            print("[entrypoint.py] RabbitMQ is ready.", flush=True)
            break
        except Exception as e:
            print(f"[entrypoint.py] Waiting for RabbitMQ... ({e})", flush=True)
            await asyncio.sleep(2)

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

    if Config.ROLE == "api":
        asyncio.run(generate_migration_if_schema_changed())
        asyncio.run(run_alembic_migrations())
        asyncio.run(initialize_db())

    # Wait for RabbitMQ
    asyncio.run(wait_for_rabbitmq())

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

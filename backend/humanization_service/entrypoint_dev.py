import subprocess
import time
from aio_pika import connect_robust
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio
from config import ROLE, RABBITMQ_URL, DATABASE_URL


role_to_command = {
    "api": ["python3", "-m", "backend.humanization_service.api.server"],
    "worker": ["python3", "-m", "backend.humanization_service.worker.humanization_worker"],
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


async def wait_for_rabbitmq(rabbitmq_url, timeout=30):
    print("[entrypoint.py wait_for_rabbitmq] Waiting for RabbitMQ...", flush=True)
    start_time = time.time()
    while True:
        try:
            connection = await connect_robust(rabbitmq_url)
            await connection.close()
            print("[entrypoint.py wait_for_rabbitmq] RabbitMQ is ready.", flush=True)
            break
        except Exception as e:
            if time.time() - start_time > timeout:
                print(f"[entrypoint.py wait_for_rabbitmq] Timeout waiting for RabbitMQ: {e}", flush=True)
                raise RuntimeError("RabbitMQ did not become ready in time.")
            print(f"[entrypoint.py wait_for_rabbitmq] Waiting for RabbitMQ... ({e})", flush=True)
            time.sleep(2)


async def run_migrations():
    """Runs Alembic migrations before starting the API."""
    print("[entrypoint.py run_migrations] Running database migrations...", flush=True)
    from backend.humanization_service.database.migrations import run_alembic_migrations
    await run_alembic_migrations()
    print("[entrypoint.py run_migrations] Migrations completed.", flush=True)


async def initialize_database():
    """Initializes the database with default data."""
    print("[entrypoint.py initialize_database] Initializing database...", flush=True)
    from backend.humanization_service.database.initialize_db import initialize_db
    await initialize_db()
    print("[entrypoint.py initialize_database] Database initialization completed.", flush=True)


def main():
    print("[entrypoint.py main] Starting main process...", flush=True)
    print(f"[entrypoint.py main] ROLE: {ROLE}", flush=True)

    if ROLE not in role_to_command:
        raise ValueError(f"[entrypoint.py main] Unsupported role: {ROLE}")
    
    if ROLE == "api":
        print(f"[entrypoint.py main] Database URL: {DATABASE_URL}", flush=True)
        asyncio.run(run_migrations())
        asyncio.run(initialize_database())

    # Wait for RabbitMQ before starting
    print(f"[entrypoint.py main] Waiting for RabbitMQ...", flush=True)
    asyncio.run(wait_for_rabbitmq(RABBITMQ_URL))
    print(f"[entrypoint.py main] --- RabbitMQ is ready", flush=True)

    # Start process with auto-reload
    print(f"[entrypoint.py main] Starting {ROLE} with auto-reload...", flush=True)
    handler = ReloadHandler(role_to_command[ROLE])
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



















import subprocess
import time
import os
import asyncio
from aio_pika import connect_robust
from backend.humanization_service.database.migrations import run_alembic_migrations
from backend.humanization_service.database.initialize_db import initialize_db

ROLE = os.getenv("ROLE")  # Read role from environment
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
DATABASE_URL = os.getenv("DATABASE_URL")

role_to_command = {
    "api": ["python3", "-m", "uvicorn", "backend.humanization_service.api.main:app", "--host", "0.0.0.0", "--port", "8000"],
    "worker": ["python3", "-m", "backend.humanization_service.worker.humanization_worker"]
}


async def wait_for_rabbitmq():
    """Waits for RabbitMQ to be available before starting services."""
    print("[entrypoint.py] Waiting for RabbitMQ...", flush=True)
    while True:
        try:
            connection = await connect_robust(RABBITMQ_URL)
            await connection.close()
            print("[entrypoint.py] RabbitMQ is ready.", flush=True)
            break
        except Exception as e:
            print(f"[entrypoint.py] Waiting for RabbitMQ... ({e})", flush=True)
            await asyncio.sleep(2)


def main():
    """Main entrypoint for API & Worker based on ROLE."""
    print(f"[entrypoint.py] Role: {ROLE}", flush=True)

    if ROLE not in role_to_command:
        raise ValueError(f"[entrypoint.py] Unsupported role: {ROLE}")

    if ROLE in ["api", "worker"]:
        asyncio.run(run_alembic_migrations())  # Ensure DB is ready

    if ROLE == "api":
        print("[entrypoint.py] Initializing database...", flush=True)
        asyncio.run(initialize_db())
        print("[entrypoint.py] Database ready.", flush=True)

    # Wait for RabbitMQ
    asyncio.run(wait_for_rabbitmq())

    # Start the service
    print(f"[entrypoint.py] Starting {ROLE}...", flush=True)
    subprocess.run(role_to_command[ROLE])


if __name__ == "__main__":
    main()

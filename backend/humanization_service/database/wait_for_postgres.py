import asyncio
import asyncpg
from core.config import Config

async def wait_for_postgres(sleep_interval=2):
    """Wait for PostgreSQL to be ready before starting the API."""
    print("[entrypoint.py] Waiting for PostgreSQL...", flush=True)
    attempts = 0
    total_wait_time = 0
    while True:
        attempts += 1
        print(f"[entrypoint.py] Attempting to connect to PostgreSQL... (Attempt {attempts}, Total wait time: {total_wait_time}s)", flush=True)
        try:
            conn = await asyncpg.connect(Config.DATABASE_URL)
            await conn.close()
            print("[entrypoint.py] PostgreSQL is ready!", flush=True)
            return
        except Exception as e:
            print(f"[entrypoint.py] PostgreSQL not ready: {e}", flush=True)
            await asyncio.sleep(sleep_interval)
            total_wait_time += sleep_interval
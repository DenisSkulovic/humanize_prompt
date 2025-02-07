from alembic import command
from alembic.config import Config
import os
import asyncio

async def run_alembic_migrations():
    """Ensures the database schema is up-to-date."""
    print("[run_alembic_migrations] Running Alembic migrations...", flush=True)
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "../alembic.ini"))
    command.upgrade(alembic_cfg, "head")
    print("[run_alembic_migrations] Alembic migrations applied successfully!", flush=True)


if __name__ == "__main__":
    asyncio.run(run_alembic_migrations())

import os
from alembic import command
from alembic.config import Config as AlembicConfig
from core.config import Config as CoreConfig

ALEMBIC_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../alembic.ini"))

async def generate_migration_if_schema_changed():
    """Generate a new migration if there are schema changes."""
    print("[generate_migration_if_schema_changed] Checking for schema changes...", flush=True)
    alembic_cfg = AlembicConfig(ALEMBIC_CONFIG_PATH)

    try:
        command.revision(alembic_cfg, autogenerate=True, message="Auto-update migration")
        print("[generate_migration_if_schema_changed] New migration generated!", flush=True)
    except Exception as e:
        print(f"[generate_migration_if_schema_changed] Migration generation failed: {e}", flush=True)

if __name__ == "__main__":
    generate_migration_if_schema_changed()
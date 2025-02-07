import os
from alembic import command
from alembic.config import Config
from run_alembic_migrations import run_alembic_migrations

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALEMBIC_CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "alembic.ini"))


def generate_migration_if_schema_changed():
    """Generate a new migration if there are schema changes."""
    print("[migrations.py] Checking for schema changes...", flush=True)
    alembic_cfg = Config(ALEMBIC_CONFIG_PATH)

    try:
        # Auto-generate a new migration based on schema changes
        command.revision(alembic_cfg, autogenerate=True, message="Auto-update migration")
        print("[migrations.py] New migration generated!", flush=True)
    except Exception as e:
        if "Target database is already up to date" in str(e):
            print("[migrations.py] No schema changes detected. Skipping migration.", flush=True)
        else:
            print(f"[migrations.py] Migration generation failed: {e}", flush=True)

if __name__ == "__main__":
    run_alembic_migrations()
    generate_migration_if_schema_changed()
import asyncio
from database.run_alembic_migrations import run_alembic_migrations
from database.insert_explanation_scales import insert_explanation_scales
from database.repository.explanation_version import ExplanationRepository
from database.database_service import DatabaseService
from database.generate_migration_if_schema_changed import generate_migration_if_schema_changed
from database.wait_for_postgres import wait_for_postgres

explanation_repository = ExplanationRepository(DatabaseService())

async def manage_db():
    await wait_for_postgres()
    
    print("[manage_db] Starting database management...", flush=True)
    await run_alembic_migrations()
    await generate_migration_if_schema_changed()
    await run_alembic_migrations()
    
    # Check if the explanations table is empty
    query = "SELECT EXISTS (SELECT 1 FROM explanation_versions)"
    result = await explanation_repository.execute_raw_query(query)
    explanations_exist = result[0][0]
    if not explanations_exist:
        await insert_explanation_scales()
    else:
        print("[manage_db] Explanations table is not empty. Skipping insertion.", flush=True)
    
    print("[manage_db] Database management complete!", flush=True)

if __name__ == "__main__":
    asyncio.run(manage_db())
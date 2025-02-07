from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

class DatabaseService:
    """
    A generic database service that abstracts database interactions using async SQLAlchemy.
    """
    def __init__(self):
        db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/mydb")
        self.engine = create_async_engine(db_url, echo=True, future=True)
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def get_session(self) -> AsyncSession:
        """
        Provides an async database session.
        """
        async with self.session_factory() as session:
            yield session

    async def execute(self, query):
        """
        Executes a query and commits the transaction.
        """
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(query)
                return result

    async def fetch_one(self, query):
        """
        Fetches a single result from the database.
        """
        async with self.session_factory() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def fetch_all(self, query):
        """
        Fetches multiple results from the database.
        """
        async with self.session_factory() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def close(self):
        """
        Closes the database connection.
        """
        await self.engine.dispose()


# Base class for SQLAlchemy models
Base = declarative_base()

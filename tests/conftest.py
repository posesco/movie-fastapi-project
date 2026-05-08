import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.main import app
from src.core.database import get_db, insert_super_user
from src.core.redis import init_redis, close_redis
from src.core.config import settings
import src.core.database as db_module

from sqlalchemy.pool import NullPool

# Use real Postgres from settings for Docker-First consistency
# No longer using SQLite in-memory to match standardized environment
TEST_DATABASE_URL = settings.async_database_url

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    # Independent engine for tests using Postgres
    # NullPool helps avoiding loop/concurrency issues with asyncpg in tests
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    
    # IMPORTANT: Initialize the database module so AsyncSessionLocal is not None
    db_module.engine = engine
    db_module.AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with engine.begin() as conn:
        # Ensure clean state for session-scoped tests
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Initialize default roles and actions
    from src.core.database import insert_default_actions, insert_default_roles
    async with db_module.AsyncSessionLocal() as session:
        await insert_default_actions(session)
        await insert_default_roles(session)
        await session.commit()
        
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(autouse=True)
async def seed_db(db_session):
    await insert_super_user(db_session)
    await db_session.commit()

@pytest_asyncio.fixture(autouse=True)
async def setup_redis():
    await init_redis()
    from src.core.redis import redis_client
    if redis_client:
        await redis_client.flushdb()
    yield
    await close_redis()

@pytest_asyncio.fixture
async def db_session(test_engine):
    async with db_module.AsyncSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    # Desactivar OTel para tests para evitar errores de conexión a alloy
    settings.otel_enabled = False

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
        yield client
    
    app.dependency_overrides.clear()

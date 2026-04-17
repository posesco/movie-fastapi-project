import os
import asyncio
import logging
from datetime import datetime, timezone
from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select
from typing import AsyncGenerator
from .config import settings
from .security import pwd_context

# Import models to ensure they are registered with SQLModel.metadata
from src.models.actions import Action
from src.models.user import Role, User, UserAuditLog, UserRole

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    url = settings.async_database_url
    host = settings.postgres_host
    # Reliable Docker detection using custom env var
    is_docker = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"
    
    if is_docker:
        logger.info("DOCKER ENVIRONMENT DETECTED: Forcing host to 'postgres'")
        password = quote_plus(settings.postgres_password)
        host = "postgres"
        url = f"postgresql+asyncpg://{settings.postgres_user}:{password}@{host}:{settings.postgres_port}/{settings.postgres_db}"
    
    # Fallback for non-docker or if URL is still empty/invalid
    if not url or "localhost" in url or "${" in url:
        if not host: host = "localhost"
        password = quote_plus(settings.postgres_password)
        url = f"postgresql+asyncpg://{settings.postgres_user}:{password}@{host}:{settings.postgres_port}/{settings.postgres_db}"

    # Final fallback to sqlite
    if not url:
        base_dir = os.path.dirname(os.path.realpath(__file__))
        sqlite_path = os.path.join(base_dir, "../../movie_api_db.sqlite")
        url = f"sqlite+aiosqlite:///{os.path.abspath(sqlite_path)}"
        
    logger.info(f"Final Connection URL: {url.replace(settings.postgres_password, '****')}")
    return url

DATABASE_URL = get_database_url()

# Initial Async Engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Async Session Factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def insert_default_actions(session: AsyncSession):
    result = await session.execute(select(Action))
    existing_actions = result.scalars().all()
    if len(existing_actions) == 0:
        actions = ["create", "update", "delete"]
        for action_name in actions:
            action = Action(name=action_name)
            session.add(action)
        await session.commit()


async def insert_default_roles(session: AsyncSession):
    result = await session.execute(select(Role))
    existing_roles = result.scalars().all()
    if len(existing_roles) == 0:
        roles = ["super_admin", "admin", "editor", "user"]
        for role_name in roles:
            role = Role(name=role_name)
            session.add(role)
        await session.commit()


async def insert_super_user(session: AsyncSession):
    result = await session.execute(
        select(User).where(User.username == settings.admin_user)
    )
    user = result.scalars().first()
    if not user:
        # Fix: Remove timezone globally for Postgres compatibility
        current_time = datetime.now().replace(microsecond=0)
        
        user_in = User(
            name="Super",
            surname="Admin",
            username=settings.admin_user,
            email=settings.admin_email,
            password=pwd_context.hash(settings.admin_pass),
            created_at=current_time
        )
        session.add(user_in)
        await session.flush()
        
        # Get role and action IDs
        role_result = await session.execute(select(Role).where(Role.name == "super_admin"))
        role = role_result.scalars().first()
        
        action_result = await session.execute(select(Action).where(Action.name == "create"))
        action = action_result.scalars().first()
        
        if role and action:
            role_in = UserRole(
                user_id=user_in.id,
                role_id=role.id,
            )
            log_in = UserAuditLog(
                user_id=user_in.id, 
                action_id=action.id, 
                description="Se creo super admin",
                date=current_time
            )
            session.add(role_in)
            session.add(log_in)
            await session.commit()


async def init_db():
    global engine, AsyncSessionLocal
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(1, max_retries + 1):
        try:
            url = get_database_url()
            engine = create_async_engine(url, echo=True, future=True)
            AsyncSessionLocal = sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )

            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
            
            async with AsyncSessionLocal() as session:
                await insert_default_actions(session)
                await insert_default_roles(session)
                await insert_super_user(session)
            
            logger.info("Database initialized successfully.")
            return
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"Failed to initialize database after {max_retries} attempts: {e}")
                raise
            logger.warning(f"Database initialization attempt {attempt} failed: {e}. Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

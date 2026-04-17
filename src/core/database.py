import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select
from typing import AsyncGenerator

from .config import settings
from .security import pwd_context

from src.models.actions import Action
from src.models.user import Role, User, UserAuditLog, UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine: AsyncEngine | None = None
AsyncSessionLocal: sessionmaker | None = None


async def insert_default_actions(session: AsyncSession) -> None:
    result = await session.execute(select(Action))
    if not result.scalars().all():
        for name in ("create", "update", "delete"):
            session.add(Action(name=name))
        await session.commit()


async def insert_default_roles(session: AsyncSession) -> None:
    result = await session.execute(select(Role))
    if not result.scalars().all():
        for name in ("super_admin", "admin", "editor", "user"):
            session.add(Role(name=name))
        await session.commit()


async def insert_super_user(session: AsyncSession) -> None:
    result = await session.execute(select(User).where(User.username == settings.admin_user))
    if result.scalars().first():
        return

    current_time = datetime.now(timezone.utc).replace(microsecond=0)
    user = User(
        name="Super",
        surname="Admin",
        username=settings.admin_user,
        email=settings.admin_email,
        password=pwd_context.hash(settings.admin_pass),
        created_at=current_time,
    )
    session.add(user)
    await session.flush()

    role_result = await session.execute(select(Role).where(Role.name == "super_admin"))
    role = role_result.scalars().first()

    action_result = await session.execute(select(Action).where(Action.name == "create"))
    action = action_result.scalars().first()

    if role and action:
        session.add(UserRole(user_id=user.id, role_id=role.id))
        session.add(UserAuditLog(
            user_id=user.id,
            action_id=action.id,
            description="Se creó super admin",
            date=current_time,
        ))

    await session.commit()


async def init_db() -> None:
    global engine, AsyncSessionLocal

    max_retries = 10
    retry_delay = 5

    for attempt in range(1, max_retries + 1):
        try:
            engine = create_async_engine(
                settings.async_database_url,
                echo=settings.project_debug_mode,
                future=True,
            )
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
                logger.error("Failed to initialize database after %d attempts: %s", max_retries, e)
                raise
            logger.warning(
                "Attempt %d/%d failed: %s. Retrying in %ds...",
                attempt, max_retries, e, retry_delay,
            )
            await asyncio.sleep(retry_delay)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select
from typing import AsyncGenerator
from .config import settings
from .security import pwd_context

# Import models to ensure they are registered with SQLModel.metadata
from src.models.actions import Action
from src.models.user import Role, User, UserAuditLog, UserRole

# Database configuration
DATABASE_URL = settings.async_database_url

if not DATABASE_URL:
    # Fallback to local sqlite if not provided (using aiosqlite for async)
    base_dir = os.path.dirname(os.path.realpath(__file__))
    sqlite_path = os.path.join(base_dir, "../../movie_api_db.sqlite")
    DATABASE_URL = f"sqlite+aiosqlite:///{os.path.abspath(sqlite_path)}"

# Async Engine
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
        user_in = User(
            name="Super",
            surname="Admin",
            username=settings.admin_user,
            email=settings.admin_email,
            password=pwd_context.hash(settings.admin_pass),
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
                description="Se creo super admin"
            )
            session.add(role_in)
            session.add(log_in)
            await session.commit()


async def init_db():
    async with engine.begin() as conn:
        # Note: SQLModel.metadata.create_all works with async connection via run_sync
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        await insert_default_actions(session)
        await insert_default_roles(session)
        await insert_super_user(session)


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

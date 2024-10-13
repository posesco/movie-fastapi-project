import os
from sqlmodel import SQLModel, create_engine, Session, select
from models.actions import Action
from models.user import Role, User, UserAuditLog, UserRole
from config.settings import settings
from config.security import pwd_context

sqlite_file_name = "movie_api_db.sqlite"
base_dir = os.path.dirname(os.path.realpath(__file__))

database_url = f"sqlite:///{os.path.join(base_dir, sqlite_file_name)}"

engine = create_engine(database_url, echo=True)


def insert_default_actions(engine):
    with Session(engine) as session:
        existing_actions = session.exec(select(Action)).all()
        if len(existing_actions) == 0:
            actions = ["create", "update", "delete"]
            for action_name in actions:
                action = Action(name=action_name)
                session.add(action)
            session.commit()


def insert_default_roles(engine):
    with Session(engine) as session:
        existing_roles = session.exec(select(Role)).all()
        if len(existing_roles) == 0:
            roles = ["super_admin", "admin", "editor", "user"]
            for role_name in roles:
                role = Role(name=role_name)
                session.add(role)
            session.commit()


def insert_super_user(engine):
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.username == settings.admin_user)
        ).first()
        if not user:
            user_in = User(
                name="Super",
                surname="Admin",
                username=settings.admin_user,
                email=settings.admin_email,
                password=pwd_context.hash(settings.admin_pass),
            )
            session.add(user_in)
            session.commit()
            session.refresh(user_in)
            user_id = user_in.id
            role_id = (
                session.exec(select(Role).where(Role.name == "super_admin")).first()
            ).id
            action_id = (
                session.exec(select(Action).where(Action.name == "create")).first()
            ).id
            role_in = UserRole(
                user_id=user_id,
                role_id=role_id,
            )
            log_in = UserAuditLog(
                user_id=user_id, action_id=action_id, description="Se creo super admin"
            )
            session.add(role_in)
            session.add(log_in)
            session.commit()


def init_db():
    SQLModel.metadata.create_all(engine)
    insert_default_actions(engine)
    insert_default_roles(engine)
    insert_super_user(engine)


def get_db():
    with Session(engine) as session:
        yield session

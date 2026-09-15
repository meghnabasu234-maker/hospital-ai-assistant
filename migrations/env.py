import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.database import Base

# Load environment variables from .env
load_dotenv()

# Import all models so Alembic can detect all tables
from app.models.user import UserDB
from app.models.department import DepartmentDB
from app.models.department_subtype import DepartmentSubtypeDB
from app.models.patient import PatientDB
from app.models.doctor import DoctorDB
from app.models.appointment import AppointmentDB
from app.models.bill import BillDB
from app.models.knowledge_document import KnowledgeDocumentDB
from app.models.knowledge_chunk import KnowledgeChunkDB
from app.models.chat_history import ChatHistoryDB
from app.models.doctor_review import DoctorReviewDB


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Read database URL from .env
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not set in the environment.")

config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
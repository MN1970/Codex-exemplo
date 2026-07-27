"""
alembic/env.py — Ambiente async do Alembic para o Manta Backend.

A URL de conexão NÃO vem do `sqlalchemy.url` do alembic.ini (que fica
com o placeholder padrão) — vem de `config.get_settings().database_url`
(mesma fonte de verdade usada pela app em runtime, incluindo `.env`),
normalizada para o driver asyncpg por `database.to_async_dsn`. Isso
evita duas configurações de DSN divergentes.

`target_metadata` aponta para `database.Base.metadata`, que registra
os 8 modelos (Organization, Role, User, Agent, RagChunk, Session,
Feedback, MLModel) — suficiente para `alembic revision --autogenerate`
detectar mudanças de schema depois desta baseline inicial.
"""
import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Garante que `manta-backend/` (pai de `alembic/`) está no sys.path,
# independente do diretório de onde `alembic` é invocado.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_settings
from database import (
    Base,
    to_async_dsn,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# DSN real vem de config.py/.env, não do alembic.ini.
config.set_main_option("sqlalchemy.url", to_async_dsn(get_settings().database_url))

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

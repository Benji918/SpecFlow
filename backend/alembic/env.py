from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, text
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.database import Base
from app.models import *
from app.config import settings
import ssl

# Create SSL context for Supabase direct connection
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use DIRECT_DATABASE_URL for migrations (bypasses PgBouncer)
# PgBouncer cannot handle DDL statements like ALTER TABLE reliably
db_url = settings.DIRECT_DATABASE_URL or settings.DATABASE_URL
if not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
config.set_main_option("sqlalchemy.url", db_url)

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
    )

    print(f"🔍 Connecting to: {config.get_main_option('sqlalchemy.url')}")

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using direct connection (no PgBouncer)."""
    
    from sqlalchemy.ext.asyncio import create_async_engine
    
    # Create engine directly with connect_args (bypasses alembic.ini config)
    connectable = create_async_engine(
        db_url,
        poolclass=pool.NullPool,
        connect_args={
            "ssl": ssl_ctx,
            "command_timeout": 300,  # 5 minute timeout for DDL operations
            "prepared_statement_cache_size": 0,  # Disable prepared statements for migrations
        },
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def do_run_migrations(connection):
   
    
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode using sync API for compatibility."""
    # Use asyncpg but in sync mode for alembic compatibility
    # This function is a fallback for SQLAlchemy 1.x compatibility 
    sync_url = config.get_main_option("sqlalchemy.url").replace("+asyncpg", "")
    config.set_main_option("sqlalchemy.url", sync_url)
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Set a longer statement timeout for migrations (5 minutes)
        connection.execute("SET statement_timeout = '300s'")
        
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    try:
        import asyncio
        asyncio.run(run_async_migrations())
    except (ImportError, TypeError, AttributeError):

        run_migrations_online()
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

import ssl

# Create robust SSL context to handle Supabase certificate mismatches
# This fixes TargetServerAttributeNotMatched errors with poolers
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,  # ✅ Increased from 2
    max_overflow=5,  # ✅ Increased from 1
    pool_pre_ping=True,
    pool_timeout=30,  # ✅ Reduced from 60
    pool_recycle=1800,  # ✅ Increased from 300 (30 min)
    connect_args={
        "statement_cache_size": 100,  # ✅ CRITICAL: Enable statement caching
        "prepared_statement_cache_size": 100,  # ✅ Enable prepared statement cache
        "ssl": ssl_ctx,
        "command_timeout": 10,  # ✅ Add query timeout
    },
    echo=False,  # Set to True for debugging
)


# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    
)

# Base class for models
Base = declarative_base()


# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

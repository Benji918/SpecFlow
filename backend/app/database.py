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
    pool_size=5, 
    max_overflow=2,  
    pool_pre_ping=True,
    pool_timeout=60,  
    pool_recycle=1800,  
    connect_args={
        "statement_cache_size": 100,  
        "prepared_statement_cache_size": 100,  
        "ssl": ssl_ctx,
        "command_timeout": 30,  
    },
    echo=False,  
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

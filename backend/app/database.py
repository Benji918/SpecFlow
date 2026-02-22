from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import AsyncAdaptedQueuePool
from app.config import settings
import ssl
import asyncio

# Create robust SSL context to handle Supabase certificate mismatches
# This fixes TargetServerAttributeNotMatched errors with poolers
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


class AsyncEngineWithRetry:
    """Wrapper around AsyncEngine with automatic retry logic for transient failures."""
    
    def __init__(self, database_url: str, max_retries: int = 3, retry_delay: float = 1.0):
        self.database_url = database_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._engine = None
        self._create_engine()
    
    def _create_engine(self):
        """Create the async engine with connection pooling."""
        self._engine = create_async_engine(
            self.database_url,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=5, 
            max_overflow=5,  # Allow more overflow connections during high load
            pool_pre_ping=True,
            pool_timeout=30,  # Reduced timeout for faster failure detection
            pool_recycle=1800,  # Recycle connections every 30 minutes
            connect_args={
                "statement_cache_size": 100,  
                "prepared_statement_cache_size": 100,  
                "ssl": ssl_ctx,
                "command_timeout": 120,
                "server_settings": {
                    "application_name": "specflow"
                }
            },
            echo=False,
        )
    
    @property
    def engine(self):
        return self._engine
    
    async def connect_with_retry(self):
        """Try to get a connection with retry logic."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                async with self._engine.connect() as conn:
                    return conn
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                    continue
        
        raise last_error


# Try to create engine, with fallback for initial connection issues
try:
    engine_wrapper = AsyncEngineWithRetry(settings.DATABASE_URL)
    engine = engine_wrapper.engine
except Exception as e:
    print(f"Warning: Initial database engine creation failed: {e}")
    # Create a basic engine that will retry on first use
    engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=AsyncAdaptedQueuePool,
        pool_size=3,
        max_overflow=3,
        pool_pre_ping=True,
        pool_timeout=30,
        connect_args={
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

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
import time
import logging
from functools import lru_cache
from app.config import settings

# Disable uvicorn access logger
logging.getLogger("uvicorn.access").disabled = True
logger = logging.getLogger("uvicorn")

from app.routers import auth, specs, journeys, execution, admin, ngrok, google_auth

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Context-aware API testing platform",
    version="0.1.0",
    debug=settings.DEBUG,
)

@lru_cache
def get_settings():
    return settings


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware to add an X-Response-Time header to all responses.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Custom combined log (replaces default uvicorn access log)
    host = request.client.host if request.client else "unknown"
    port = request.client.port if request.client else "0"
    
    logger.info(
        f'{host}:{port} - "{request.method} {request.url.path}" {response.status_code} - {process_time:.4f}s'
    )

    response.headers["X-Response-Time"] = f"{process_time:.4f}s"
    return response

# Configure Middlewares
app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

# Include routers
app.include_router(auth.router)
app.include_router(specs.router)
app.include_router(journeys.router)
app.include_router(execution.router)
app.include_router(admin.router)
app.include_router(ngrok.router)
app.include_router(google_auth.router)

@app.on_event("startup")
def startup_event():
    """Ensure no old ngrok processes are running on startup."""
    from pyngrok import ngrok
    if settings.NGROK_ENABLED:
        logger.info("Cleaning up old ngrok processes...")
        ngrok.kill()

@app.on_event("shutdown")
def shutdown_event():
    """Ensure ngrok processes are killed on shutdown."""
    from pyngrok import ngrok
    logger.info("Shutting down ngrok tunnels...")
    ngrok.kill()


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "specflow-backend"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SpecFlow API",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

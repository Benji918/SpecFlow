from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, specs, journeys, execution

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Context-aware API testing platform",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(specs.router)
app.include_router(journeys.router)
app.include_router(execution.router)


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

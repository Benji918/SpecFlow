from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

from app.config import settings
from app.routers import auth, specs, journeys, execution

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Context-aware API testing platform",
    version="0.1.0",
    debug=settings.DEBUG,
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware to add an X-Response-Time header to all responses.
    """
    start_time = time.time()
    response = await call_next(request)  # Process the actual request
    end_time = time.time()
    process_time = end_time - start_time
    # Format the time (e.g., to milliseconds or just seconds)
    response.headers["X-Response-Time"] = f"{process_time:.4f}s"
    return response

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

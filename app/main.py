"""
Main FastAPI application initialization and configuration.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title="Dashcam Backend API",
    description="Backend API for dashcam incident reporting and video processing",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    """
    Root endpoint with API information.
    
    Returns:
        API welcome message and version
    """
    return {
        "message": "Dashcam Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "healthy"}

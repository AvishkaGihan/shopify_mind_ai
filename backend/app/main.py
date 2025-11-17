"""
FastAPI application initialization and configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from app.config import get_settings
from app.database import get_database
from app.utils.error_handler import handle_exceptions
from app.utils.logger import get_logger
from app.routers import (
    auth_router,
    products_router,
    chat_router,
    orders_router,
    store_router,
    analytics_router,
)

logger = get_logger(__name__)
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="ShopifyMind AI API",
    description="AI-powered e-commerce chatbot backend with product recommendations and order tracking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
handle_exceptions(app)

# Include routers
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(chat_router)
app.include_router(orders_router)
app.include_router(store_router)
app.include_router(analytics_router)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.

    Initialize services and log startup information.
    """
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API host: {settings.api_host}:{settings.api_port}")

    # Test database connection
    db = get_database()
    is_healthy = await db.health_check()

    if is_healthy:
        logger.info("Database connection successful")
    else:
        logger.error("Database connection failed")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.

    Clean up resources and log shutdown.
    """
    logger.info(f"Shutting down {settings.app_name}")


@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint",
    description="Get API status and basic information.",
)
async def root():
    """
    Root endpoint returning API status.
    """
    return {
        "success": True,
        "data": {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "operational",
            "docs": "/docs",
            "redoc": "/redoc",
        },
        "message": "ShopifyMind AI API is running",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if API and database are healthy.",
)
async def health_check():
    """
    Health check endpoint.

    Returns:
    - API status
    - Database connection status
    - Timestamp
    """
    db = get_database()
    db_healthy = await db.health_check()

    status_code = 200 if db_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "success": db_healthy,
            "data": {
                "api": "healthy",
                "database": "healthy" if db_healthy else "unhealthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        },
    )


@app.get(
    "/version",
    tags=["Health"],
    summary="Get API version",
    description="Get current API version and build information.",
)
async def get_version():
    """
    Get API version information.
    """
    return {
        "success": True,
        "data": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": "development" if settings.debug else "production",
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


__all__ = ["app"]

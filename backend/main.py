"""
Entry point for running the FastAPI application.

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

# This allows running with: python main.py
if __name__ == "__main__":
    import uvicorn
    from app.config import get_settings

    settings = get_settings()

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )

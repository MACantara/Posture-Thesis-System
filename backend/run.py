import os
import uvicorn

from app.config import settings


if __name__ == "__main__":
    # Use reload only in development (not in Railway/production)
    reload = os.getenv("RAILWAY_ENVIRONMENT") is None and os.getenv("ENVIRONMENT") != "production"
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=reload,
    )

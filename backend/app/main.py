from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db.factory import get_repositories
from app.routers import auth as auth_router
from app.routers import posture as posture_router
from app.routers import sessions as sessions_router
from app.routers import users as users_router
from app.routers import sensors as sensors_router
from app.routers import websocket as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database based on backend
    if settings.DB_BACKEND == "sqlite":
        from app.db.sqlite.connection import init_db
        await init_db(settings.db_path)
    elif settings.DB_BACKEND == "postgresql":
        from app.db.postgresql.connection import init_db
        await init_db(settings.DATABASE_URL)
    
    repos = get_repositories()
    app.state.repos = repos

    from app.seed.seed_data import seed_if_empty
    await seed_if_empty(repos)

    yield


app = FastAPI(
    title="Posture Thesis System",
    description="Wearable sensor-based posture detection and real-time feedback correction",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


app.include_router(auth_router.router)
app.include_router(posture_router.router)
app.include_router(sessions_router.router)
app.include_router(users_router.router)
app.include_router(ws_router.router)
app.include_router(sensors_router.router)

# Serve built React frontend as static files (SPA fallback to index.html)
frontend_dist = Path(settings.FRONTEND_DIST_PATH)
if frontend_dist.exists() and frontend_dist.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=str(frontend_dist), html=True),
        name="frontend",
    )

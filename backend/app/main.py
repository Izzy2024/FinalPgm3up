import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import Base, engine
from app.api.routes import auth, users, articles, recommendations, annotations
from app.models import User, Article, Category, UserLibrary, Recommendation, Annotation

settings = get_settings()

app = FastAPI(
    title="SIGRAA API",
    description="Sistema de Gestión y Recomendación de Artículos Académicos",
    version="0.1.0",
)


def run_database_migrations() -> None:
    """Ensure the latest Alembic migrations are applied before serving requests."""
    base_path = Path(__file__).resolve().parents[1]
    alembic_cfg = Config(str(base_path / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(base_path / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    logger = logging.getLogger("alembic_runtime")
    try:
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations applied successfully.")
    except Exception:
        logger.exception("Failed to apply database migrations")
        raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(articles.router)
app.include_router(recommendations.router)
app.include_router(annotations.router)


@app.on_event("startup")
def startup_event():
    run_database_migrations()


@app.get("/")
def root():
    return {
        "message": "SIGRAA API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.backend_host, port=settings.backend_port)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import Base, engine
from app.api.routes import auth, users, articles, recommendations
from app.models import User, Article, Category, UserLibrary, Recommendation

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SIGRAA API",
    description="Sistema de Gestión y Recomendación de Artículos Académicos",
    version="0.1.0",
)

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

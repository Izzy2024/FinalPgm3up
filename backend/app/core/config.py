from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    backend_port: int = 8000
    backend_host: str = "0.0.0.0"
    debug: bool = True

    database_url: str = "postgresql://sigraa_user:sigraa_password@localhost:5432/sigraa_db"
    sqlalchemy_echo: bool = False

    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    groq_api_key: Optional[str] = None

    max_file_size: int = 52428800
    allowed_extensions: str = "pdf,txt"

    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()

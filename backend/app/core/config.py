import json
from functools import lru_cache
from typing import List, Optional, Union

from pydantic import field_validator
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

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip().strip("'").strip('"')
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return []

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()

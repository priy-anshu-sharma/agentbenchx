"""Application configuration module."""

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings
from typing import List, Union


class Settings(BaseSettings):
    PROJECT_NAME: str = "AgentBenchX"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = []

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "agentbenchx"
    POSTGRES_PASSWORD: str = "agentbenchx_password"
    POSTGRES_DB: str = "agentbenchx"
    DATABASE_URL: PostgresDsn = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Union[str, None], info) -> PostgresDsn:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_SERVER"),
            port="5432",
            path=f"/{info.data.get('POSTGRES_DB') or ''}",
        )

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # Email settings (for future use)
    # SMTP_TLS: bool = True
    # SMTP_PORT: Optional[int] = None
    # SMTP_HOST: Optional[str] = None
    # SMTP_USER: Optional[str] = None
    # SMTP_PASSWORD: Optional[str] = None
    # EMAILS_FROM_EMAIL: Optional[str] = None
    # EMAILS_FROM_NAME: Optional[str] = None

    # Email reset token expire time
    # EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    # Files related
    # MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
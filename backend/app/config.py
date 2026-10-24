from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate .env file relative to this file: backend/.env
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables and .env file.
    """
    app_name: str = Field(default="Student Skill Gap Analyzer", validation_alias="APP_NAME")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    database_url: str = Field(default="sqlite:///./app.db", validation_alias="DATABASE_URL")
    jwt_secret: str = Field(
        default="dev_secret_key_student_skill_gap_analyzer_only",
        validation_alias="JWT_SECRET",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    frontend_origin: str = Field(
        default="http://localhost:5173",
        validation_alias="FRONTEND_ORIGIN",
    )
    job_freshness_days: int = Field(
        default=30,
        validation_alias="JOB_FRESHNESS_DAYS",
        description="Threshold in days after which a posting is flagged as stale",
    )

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH) if ENV_PATH.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ("production", "prod")


settings = Settings()

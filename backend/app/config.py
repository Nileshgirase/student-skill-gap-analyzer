from pathlib import Path
from pydantic import Field, field_validator
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
        default=10080,  # 7 days (10080 minutes) to ensure persistent student sessions across visits
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
    # Optional SMTP configuration for email delivery
    smtp_host: str | None = Field(default=None, validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, validation_alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, validation_alias="SMTP_PASSWORD")
    smtp_from_email: str = Field(
        default="noreply@skillgap.analyzer",
        validation_alias="SMTP_FROM_EMAIL",
    )

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH) if ENV_PATH.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("database_url", mode="after")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        # 1. Normalize Render/Heroku postgres:// URLs to postgresql://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        # 2. Fix relative SQLite paths to always point to BASE_DIR / app.db
        if v.startswith("sqlite:///") and not v.startswith("sqlite:////") and ":memory:" not in v:
            relative_path = v.replace("sqlite:///", "")
            if relative_path.startswith("./") or not Path(relative_path).is_absolute():
                clean_rel = relative_path.lstrip("./")
                abs_db_path = (BASE_DIR / clean_rel).resolve()
                v = f"sqlite:///{abs_db_path.as_posix()}"
        return v

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ("production", "prod")


settings = Settings()

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://gradeops:gradeops@localhost:5432/gradeops"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    gcs_bucket_name: str = "gradeops-exams"
    google_application_credentials: str = ""

    anthropic_api_key: str = ""

    environment: str = "development"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Reride"
    debug: bool = True
    api_prefix: str = "/api/v1"

    # Database
    database_url: str = "sqlite+aiosqlite:///./reride.db"

    # Use Celery for async tasks (set to False for local dev without Redis)
    use_celery: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    secret_key: str = "CHANGE-THIS-IN-PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # AWS S3
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-northeast-2"
    s3_bucket_name: str = "reride-videos"

    # File Upload
    max_video_size_mb: int = 100
    allowed_video_types: list[str] = ["video/mp4", "video/quicktime", "video/x-msvideo"]

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()

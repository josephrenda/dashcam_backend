"""
Core configuration module for the Dashcam Backend API.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_SECRET_KEY: str
    API_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database Configuration
    DATABASE_URL: str
    MYSQL_ROOT_PASSWORD: Optional[str] = None
    MYSQL_DATABASE: Optional[str] = None
    MYSQL_USER: Optional[str] = None
    MYSQL_PASSWORD: Optional[str] = None
    
    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    # OSRM Configuration
    OSRM_HOST: str = "osrm-backend"
    OSRM_PORT: int = 5000
    OSRM_URL: str = "http://osrm-backend:5000"
    
    # Video Storage
    VIDEO_STORAGE_PATH: str = "/var/data/videos"
    MAX_VIDEO_SIZE_MB: int = 500
    
    # ML Models
    YOLO_MODEL: str = "yolov8n.pt"
    OCR_LANGUAGES: str = "en"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

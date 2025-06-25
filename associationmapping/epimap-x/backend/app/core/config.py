from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # SQLite for local development
    DATABASE_URL: str = "sqlite:///./epimap.db"
    REDIS_URL: str = "redis://localhost:6379"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "epimap-data"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Local file storage fallback
    LOCAL_STORAGE_PATH: str = "./uploads"

    class Config:
        env_file = ".env"

settings = Settings()
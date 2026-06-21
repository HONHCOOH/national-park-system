import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "国家公园智能决策支持系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "*"]

    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "national_park"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    LLM_PROVIDER: str = "deepseek"
    LLM_MODEL: str = "qwen2.5:7b"
    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_API_KEY: str = ""

    FIRMS_MAP_KEY: str = ""

    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = "utf-8"


settings = Settings()

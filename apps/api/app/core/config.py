from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_EXP_MIN: int = 60
    OPENAI_API_KEY: str | None = None
    ELEVENLABS_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file="apps/api/.env", env_file_encoding="utf-8")

settings = Settings()

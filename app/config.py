from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Указываем абсолютный путь к файлу
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / "app/.env"),
        env_file_encoding="utf-8"
    )


settings = Settings()

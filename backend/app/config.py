from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # PostgreSQL
    POSTGRES_HOST: str = "postgre"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "izanagi_user"
    POSTGRES_PASSWORD: str = "izanagi_pass"
    POSTGRES_DB: str = "izanagi_db"

    # MongoDB
    MONGO_HOST: str = "mongo"
    MONGO_PORT: int = 27017

    # JWT
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    model_config = SettingsConfigDict(
        env_file="../.env",
        case_sensitive=True
    )

    @property
    def JWT_PRIVATE_KEY(self) -> str:
        path = Path("/app/private_key.pem")
        if not path.exists():
            raise RuntimeError("JWT private key not found at /app/private_key.pem")
        return path.read_text()

    @property
    def JWT_PUBLIC_KEY(self) -> str:
        path = Path("/app/public_key.pem")
        if not path.exists():
            raise RuntimeError("JWT public key not found at /app/public_key.pem")
        return path.read_text()


settings = Settings()

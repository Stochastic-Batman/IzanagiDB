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
    JWT_SECRET_KEY: str = "oM2zFvsrH9UtEiolhbZoVe-dPbyOzEHZNIwntMHuzk0"
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    tables_config = SettingsConfigDict(
        env_file="../.env",
        case_sensitive=True
    )


settings = Settings()

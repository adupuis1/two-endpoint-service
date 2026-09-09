from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra= "ignore"
    )

    PROJECT_NAME: str = "Two-Endpoint Service"
    DATABASE_URL: str = "postgresql+psycopg://postgres:dev@localhost:5432/postgres"

settings = Settings()
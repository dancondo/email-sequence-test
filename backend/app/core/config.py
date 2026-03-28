from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://jooba:jooba_dev_password@db:5432/jooba"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 9090

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

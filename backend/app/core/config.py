from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://jooba:jooba_dev_password@db:5432/jooba"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 9090

    NYLAS_CLIENT_ID: str = ""
    NYLAS_API_KEY: str = ""
    NYLAS_API_URI: str = "https://api.us.nylas.com"
    NYLAS_REDIRECT_URI: str = "http://localhost:9090/api/email-integration/callback"
    NYLAS_WEBHOOK_SECRET: str = ""
    FRONTEND_URL: str = "http://localhost:9000"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

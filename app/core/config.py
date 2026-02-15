from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "FINAGLE_"}

    database_url: str = "sqlite:///finagle.db"
    api_key: str = ""
    environment: str = "dev"
    max_upload_mb: int = 10


settings = Settings()

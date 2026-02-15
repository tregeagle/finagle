from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "FINAGLE_"}

    database_url: str = "sqlite:///finagle.db"


settings = Settings()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Music Tools"
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"


settings = Settings()

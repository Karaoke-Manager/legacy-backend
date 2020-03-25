from pydantic import BaseSettings


class Settings(BaseSettings):
    application_name: str
    openapi_path: str
    debug: bool

    database_url: str

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_prefix = ""


settings = Settings()

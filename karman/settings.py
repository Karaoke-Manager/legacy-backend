import sys

from pydantic import BaseSettings


class Settings(BaseSettings):
    application_name: str
    openapi_path: str
    debug: bool
    test: bool = "pytest" in sys.modules

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_issuer: str

    class Config:
        case_sensitive = False
        env_file = ".env.testing" if "pytest" in sys.modules else ".env"
        env_prefix = ""


settings = Settings()

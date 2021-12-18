from fastapi.security import OAuth2PasswordBearer

from karman.config import app_config

oauth2_password_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{app_config.oauth2_path}/{app_config.oauth2_password_endpoint}",
    description="Authenticate against the local Karman user database.",
    scheme_name="Password Login",
)

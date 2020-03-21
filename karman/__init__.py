from flask_jwt_extended import JWTManager

from .models import db  # noqa: F401
from .rest import api  # noqa: F401

jwt = JWTManager()

from flask_jwt_extended import JWTManager

from .models import db
from .rest import api

jwt = JWTManager()

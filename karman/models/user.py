from werkzeug.security import generate_password_hash, check_password_hash

from .database import db


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.Text(), nullable=False, unique=True)
    password_hash = db.Column(db.Text())

    def __init__(self, **kwargs):
        if "password" in kwargs:
            password = kwargs["password"]
            del kwargs["password"]
        else:
            password = None
        super().__init__(**kwargs)
        if password:
            self.set_password(password)

    def set_password(self, password: str) -> str:
        hashed = generate_password_hash(password)
        self.password_hash = hashed
        return hashed

    def validate_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

from sqlalchemy.orm import Session

from karman import models
from karman.models import User

UNUSED_USERNAME = "absent"


class TestDataset:
    def user_count(self, db: Session):
        return db.query(User).count()

    def load(self, db: Session):
        db.commit()


class SingleUserDataset(TestDataset):
    def __init__(self):
        self.user = models.User(username="user", password="password1")

    def load(self, db: Session):
        db.add(self.user)
        super().load(db)

    def user_exists(self, db: Session):
        return db.query(User).get(self.user.id) is not None


class MultiUserDataset(TestDataset):
    def __init__(self):
        self.users = [
            User(username="user1", password="password1"),
            User(username="user2", password="password1")
        ]

    def load(self, db: Session):
        for user in self.users:
            db.add(user)
        super().load(db)


class RealDataset(TestDataset):
    def __init__(self):
        self.admin = User(username="admin", password="password", is_admin=True)

    def load(self, db: Session):
        db.add(self.admin)
        super().load(db)

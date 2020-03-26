from sqlalchemy.orm import Session

from karman.models import User, Role
from karman.scopes import MANAGE_LIBRARY


class Dataset:
    UNUSED_USERNAME = "absent"
    UNUSED_ROLE = "absent"
    ADMIN_PASSWORD = "password"

    def __init__(self):
        self.manager_role = Role(name="Manager", scopes=[MANAGE_LIBRARY])

        self.admin = User(username="admin", password=Dataset.ADMIN_PASSWORD, is_admin=True)
        self.users = [
            User(username="user1", password="password1"),
            User(username="user2", password="password1", roles=[self.manager_role])
        ]

    def user_count(self, db: Session):
        return db.query(User).count()

    def load(self, db: Session):
        db.add(self.manager_role)
        db.add(self.admin)
        for user in self.users:
            db.add(user)
        db.commit()

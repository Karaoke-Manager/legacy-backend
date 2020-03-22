from karman.models import User
from karman.models.database import get_or_create

UNUSED_USERNAME = "absent"


class TestDataset:
    def user_count(self):
        return User.query.count()


class SingleUserDataset(TestDataset):
    def __init__(self):
        self.user = get_or_create(User, search="username", username="user", password="password1")

    def user_exists(self):
        return User.query.filter_by(id=self.user.id).count() == 1


class MultiUserDataset(TestDataset):
    def __init__(self):
        self.user1 = get_or_create(User, search="username", username="user1", password="password1")
        self.user2 = get_or_create(User, search="username", username="user2", password="password1")

    @property
    def users(self):
        return [self.user1, self.user2]

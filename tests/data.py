from karman.models import User, db

UNUSED_USERNAME = "absent"


class TestDataset:
    def __init__(self):
        db.session.commit()

    def user_count(self):
        return User.query.count()


class SingleUserDataset(TestDataset):
    def __init__(self):
        self.user = User.get_or_create(search="username", username="user", password="password1")
        super().__init__()

    def user_exists(self):
        return User.query.filter_by(id=self.user.id).count() == 1


class MultiUserDataset(TestDataset):
    def __init__(self):
        self.user1 = User.get_or_create(search="username", username="user1", password="password1")
        self.user2 = User.get_or_create(search="username", username="user2", password="password1")
        super().__init__()

    @property
    def users(self):
        return [self.user1, self.user2]


class RealDataset(TestDataset):
    def __init__(self):
        self.admin = User.get_or_create(search="username", username="admin", password="password", is_admin=True)
        super().__init__()

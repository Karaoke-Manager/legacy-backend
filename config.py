import os

project_root = os.path.dirname(os.path.abspath(__file__))

# SQLAlchemy Configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(project_root, 'db.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# JWT Configuration
JWT_SECRET_KEY = 'THIS IS A KEY THAT SHOULD BE CHANGED IN PRODUCTION'

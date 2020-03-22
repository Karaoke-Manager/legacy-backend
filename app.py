from flask import Flask
from flask_migrate import Migrate
from flask_talisman import Talisman

import config
from karman import jwt
from karman.cli import user_command
from karman.models import db
from karman.rest import api


def create_app(extra_config=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)
    if isinstance(extra_config, dict):
        app.config.from_mapping(extra_config)
    else:
        app.config.from_object(extra_config)

    db.init_app(app)
    jwt.init_app(app)
    api.init_app(app)
    if not app.testing:
        Talisman(app)
        Migrate(app, db)

    app.cli.add_command(user_command)

    return app

from flask import Flask
from flask_migrate import Migrate
from flask_talisman import Talisman

import config
from karman import db, api, jwt


def create_app(extra_config=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)
    if extra_config:
        app.config.from_object(extra_config)

    db.init_app(app)
    jwt.init_app(app)
    api.init_app(app)
    Talisman(app)

    Migrate(app, db)
    return app

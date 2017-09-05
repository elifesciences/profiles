from flask import Flask
from profiles.api.ping import PING_BP


def create_app() -> Flask:
    app = Flask(__name__)

    app.register_blueprint(PING_BP)

    return app

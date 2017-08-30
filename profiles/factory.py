from flask import Flask
from .api import ping_bp


def create_app():
    app = Flask(__name__)

    app.register_blueprint(ping_bp)

    return app

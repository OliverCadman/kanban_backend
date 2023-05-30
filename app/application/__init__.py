from flask import Flask
from flask_jwt_extended import JWTManager


from application.users.views import users as user_bp
from application.boards.views import boards as boards_bp
from application.database import mongo
from application.mail import mailing


from application.config import Config


def create_app(default_config=Config):
    """Define the Flask Application"""

    app = Flask(__name__)


    app.config.from_object(default_config)
    mongo.init_app(app)
    mailing.init_app(app)

    JWTManager(app)

    app.register_blueprint(user_bp)
    app.register_blueprint(boards_bp)

    return app

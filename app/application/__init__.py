from flask import Flask
from flask_pymongo import PyMongo
from flask_mail import Mail
from flask_jwt_extended import JWTManager

from application.users.views import users as user_bp
from application.database import mongo
from application.mail import mailing

from exceptions.handlers import EmailExistsError

import os

from application.config import Config


def create_app(default_config=Config):
    """Define the Flask Application"""

    app = Flask(__name__)
    app.config.from_object(default_config)
    mongo.init_app(app)
    mailing.init_app(app)

    jwt = JWTManager(app)

    app.register_blueprint(user_bp)

    return app

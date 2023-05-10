from flask import Flask
from flask_pymongo import PyMongo

from application.users.views import users as user_bp
from application.database import mongo

import os



def create_app():
    """Define the Flask Application"""

    app = Flask(__name__)
    app.config["MONGO_URI"] = (
    "mongodb://"
    + os.environ["MONGODB_USERNAME"]
    + ":"
    + os.environ["MONGODB_PASSWORD"]
    + "@"
    + os.environ["MONGODB_HOSTNAME"]
    + ":27017/"
    + os.environ["MONGODB_DATABASE"]
    )   
    app.config["TESTING"] = True

    mongo.init_app(app)
    app.register_blueprint(user_bp)

    return app

"""Configuration for the Flask Application"""


import os


class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY")
    MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE")
    MONGO_URI = ("mongodb://"
    + os.environ["MONGODB_USERNAME"]
    + ":"
    + os.environ["MONGODB_PASSWORD"]
    + "@"
    + os.environ["MONGODB_HOSTNAME"]
    + ":27017/"
    + os.environ["MONGODB_DATABASE"]
    )
    
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT"))
    MAIL_USE_TLS = bool(int(os.environ.get("MAIL_USE_TLS")))
    MAIL_USE_SSL = bool(int(os.environ.get("MAIL_USE_SSL")))
    MAIL_DEBUG = bool(os.environ.get("MAIL_DEBUG"))
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

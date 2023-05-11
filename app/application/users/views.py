from flask import Response, Blueprint, request, jsonify, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from application.users.controllers import User
from exceptions.handlers import (
    EmailExistsError,
    EmailValidationError,
    PasswordTooShortError,
    PasswordCharacterCaseError,
    PasswordDigitError,
    PasswordSpecialCharacterError
    )
from application.users.messaging import send_email

import json
from bson.objectid import ObjectId
from bson import json_util

from application.users.token import generate_token, confirm_token
from application.database import mongo

users = Blueprint("users", __name__)


def parse_json(data):
    """
    Helper function to serialize a User object.
    Required since ObjectId is non-JSON serializable.
    """
    return json.loads(json_util.dumps(data))


@users.route('/user_profile', methods=['GET'])
@jwt_required()
def user_profile():
    user_email = get_jwt_identity()
    user = User.find_user_no_password(user_email)
    return parse_json(user), 200


@users.route('/register', methods=["POST"])
def register():
    """Register a user"""
    if request.method == 'POST':
        data = request.json

        username = data["username"]
        email = data["email"]
        password = data["password"]


        try:
            new_user = User(username=username, email=email, password=password)
            new_user.register()
            token =  generate_token(new_user.email)
            confirm_url = f"127.0.0.1:8000/confirm_email/{token}"
            subject = 'Please confirm your email address.'
            send_email(
                new_user.email,
                subject,
                url=confirm_url
            )

        except EmailValidationError:
            return ("Email is invalid.", 400)
        except EmailExistsError:
            return ("Email already exists.", 400)
        except PasswordTooShortError:
            return ("Password is too short.", 400)
        except PasswordCharacterCaseError:
            return (
                "Your password should contain at least one uppercase letter.",
                400
                )
        except PasswordDigitError:
            return (
                "Your password should contain at least one number.",
                400
            )
        except PasswordSpecialCharacterError:
            return (
                "Your password should contain at least one special character.",
                400
            )

        data['token'] = token
        return (jsonify(data), 201)

@users.route('/confirm_email/<token>')
def confirm_email(token):
    """
    Feed the token provided in the URL param into the confirm_token function.
    confirm_token should return the email address associated with the user
    who owns the token.

    If so, update the 'is_confirmed' status of the user object in DB.
    If not, return 400 error.
    """
    email = confirm_token(token)

    user = mongo.db.users.find_one({"email": email})

    if user and user['email'] == email:
        User.update_email_verification_status(user['_id'])
        return parse_json(user), 200
    else:
        return jsonify({
            'msg': 'The link is either invalid or has expired.'
        }), 400


@users.route('/login', methods=['POST'])
def login():
    """
    Route to log a user in.
    Creates a JWT token if user validated correctly.
    Otherwise, return a 400 error.
    """
    if request.method == 'POST':
        data = request.json
        email = data['email']
        password = data['password']

        if not data or not password:
            return jsonify({
                'msg': 'Please provide an email/password,'
            })
        
        user = User.find_user_by_email(email)
        if user:
            password_check = User.check_password(user['password'], password)
            if password_check:
                token = create_access_token(identity=email)
  
                return jsonify(token=token), 200
            else:
                return jsonify({
                    'msg': 'Your password is invalid.'
                }), 401
            

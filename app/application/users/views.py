from flask import Blueprint, request, jsonify, session, make_response
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    set_access_cookies
    )
from application.users.models import User
from exceptions.handlers import (
    EmailExistsError,
    EmailValidationError,
    PasswordTooShortError,
    PasswordCharacterCaseError,
    PasswordDigitError,
    PasswordSpecialCharacterError,
    InvalidAPIUsage
    )
from application.users.messaging import send_email

from application.helpers import parse_json

from application.users.token import generate_token, confirm_token
from application.database import mongo


from datetime import datetime, timezone, timedelta


users = Blueprint("users", __name__)

CORS(users, supports_credentials=True, resources=r"*")


@users.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


# @users.after_request
# def cookie_middleware(response):
#     response.headers.add("Access-Control-Allow-Credentials", "true")
#     print("RESPONSE AFTER REQUEST:", response)
#     return response


@users.route('/')
def index():
    return jsonify({"msg": "Hello World!!"})


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
            session["user_email"] = new_user.email
            token =  generate_token(new_user.email)


            data['token'] = token
            response = jsonify(token=data)

            confirm_url = f"127.0.0.1:8000/confirm_email/{token}"
            subject = 'Please confirm your email address.'
            # send_email(
            #     new_user.email,
            #     subject,
            #     url=confirm_url
            # )

        except EmailValidationError:
            error_msg = jsonify(msg="Email address is invalid.")
            error_msg.headers.add('Access-Control-Allow-Origin', '*')
            return 
        except EmailExistsError:
            error_msg = jsonify(msg="Email already exists.")
            error_msg.headers.add('Access-Control-Allow-Origin', '*')
            return (error_msg, 400)
        except PasswordTooShortError:
            error_msg = jsonify(msg="Your password is too short.")
            return error_msg, 400
        except PasswordCharacterCaseError:
            error_msg = jsonify(msg="Your password should contain at least one uppercase letter.")
            error_msg.headers.add('Access-Control-Allow-Origin', '*')
            return error_msg, 400
        except PasswordDigitError:
            error_msg = jsonify(msg="Your password should contain at least one number.")
            error_msg.headers.add('Access-Control-Allow-Origin', '*')
            return error_msg, 400
        except PasswordSpecialCharacterError:
            error_msg = jsonify(msg="Your password should contain at least one special character.")
            response = make_response(error_msg, 400)
            response.headers["Content-Type"] = 'application/json'
            return make_response(error_msg, 400)
        
        return (response, 201)

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
                response = jsonify(token=token)
                cookies = set_access_cookies(response, token)

                session["user_email"] = email

                return response, 200
            else:
                return jsonify({
                    'msg': 'Your password is invalid.'
                }), 400
            

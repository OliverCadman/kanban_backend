from flask import Response, Blueprint, request
from application.users.controllers import User
from exceptions.handlers import (
    EmailExistsError,
    EmailValidationError,
    PasswordTooShortError,
    PasswordCharacterCaseError,
    PasswordDigitError,
    PasswordSpecialCharacterError
    )

import json

users = Blueprint("users", __name__)


@users.route('/user_profile')
def user_profile():
    return 'User Profile'


@users.route('/register', methods=["POST"])
def register():
    if request.method == 'POST':
        data = request.json

        username = data["username"]
        email = data["email"]
        password = data["password"]


        try:
            new_user = User(username=username, email=email, password=password)
            new_user.register()
        except EmailValidationError:
            return Response("Email is invalid.", status=400)
        except EmailExistsError:
            return Response("Email already exists.", status=400)
        except PasswordTooShortError:
            return Response("Password is too short.", status=400)
        except PasswordCharacterCaseError:
            return Response(
                "Your password should contain at least one uppercase letter.",
                status=400
                )
        except PasswordDigitError:
            return Response(
                "Your password should contain at least one number.",
                status=400
            )
        except PasswordSpecialCharacterError:
            return Response(
                "Your password should contain at least one special character.",
                status=400
            )

        return Response(data, status=201)

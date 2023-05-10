from flask import Response, Blueprint, request
from application.users.controllers import User

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

        new_user = User(username=username, email=email, password=password)
        registration_attempt = new_user.register()

        if registration_attempt:
            return Response(json.dumps(data), status=201)
        else:
            return Response(status=400)


        return Response(status=200)

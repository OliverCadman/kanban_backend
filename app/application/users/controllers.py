

from werkzeug.security import generate_password_hash
from exceptions.handlers import (
    EmailExistsError,
    EmailValidationError,
    PasswordTooShortError,
    PasswordCharacterCaseError,
    PasswordDigitError,
    PasswordSpecialCharacterError
    )
from application.database import mongo
import requests
from requests.structures import CaseInsensitiveDict
import os

import re
import json
from bson.objectid import ObjectId


class User:
    """Controller for the User object."""

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.is_confirmed = False
    
    def _get_user_profile(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "is_confirmed": self.is_confirmed
        }

    def _check_user_exists(self, email):
        """
        Query DB for user with given email.
        If one exists, return True.
        """

        existing_user = mongo.db.users.find_one({"email": email})

        if existing_user:
            raise EmailExistsError()
        else:
            return False
    
    @staticmethod
    def _validate_email(email):
        return True
        # TODO: Re-ignite this code when the time comes!!!
        # url = f"https://api.emailvalidation.io/v1/info?email={email}"

        # headers = CaseInsensitiveDict()
        # headers["apikey"] = os.environ.get('VALIDATE_EMAIL_API_KEY')

        # res = requests.get(url, headers=headers)

        # res_json = res.content.decode('utf8').replace("'", '"')
        # data = json.loads(res_json)
        # formatted = json.dumps(data, indent=4, sort_keys=True)
        # print(data)

        # if data.get("message") == "Validation error":
        #     raise EmailValidationError()
        # else:
        #     return True

    @staticmethod
    def _check_password_valid(password):
        """
        Check if the password satisfies the following criteria:
            More than 8 letters
            Has at least one capital letter
            Has at least one number
            Has at least one special character
        """

        if len(password) < 8:
            raise PasswordTooShortError()
        elif re.search('[0-9]', password) is None:
            raise PasswordDigitError()
        elif re.search('[A-Z]', password) is None:
            raise PasswordCharacterCaseError()
        elif re.search('[@_!#$%^&*()<>?/\|}{~:]', password) is None:
            raise PasswordSpecialCharacterError()
        else:
            return True
    
    def register(self):
        user_data = self._get_user_profile()

        self._validate_email(user_data["email"])

        user_exists = self._check_user_exists(user_data["email"])

        if not user_exists:
            if self._check_password_valid(user_data['password']):
                user_data["password"] = generate_password_hash(
                    user_data['password'])
                mongo.db.users.insert_one(user_data)
    
    @staticmethod
    def update_email_verification_status(user_id):

        mongo.db.users.update_one({
            "_id": user_id,
        },{
              "$set": {
                "is_confirmed": True
            }
        })

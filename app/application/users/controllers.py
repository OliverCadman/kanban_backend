

from werkzeug.security import generate_password_hash
from exceptions.handlers import (
    EmailExistsError,
    PasswordTooShortError,
    PasswordCharacterCaseError,
    PasswordDigitError,
    PasswordSpecialCharacterError
    )
from application.database import mongo

import re

class User:

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
    
    def _get_user_profile(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password
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

        user_exists = self._check_user_exists(user_data["email"])

        if not user_exists:
            if self._check_password_valid(user_data['password']):
                user_data["password"] = generate_password_hash(
                    user_data['password'])
                mongo.db.users.insert_one(user_data)

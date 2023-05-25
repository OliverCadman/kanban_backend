from werkzeug.exceptions import BadRequest


class EmailExistsError(BadRequest):
    code = 400
    description = "A user with that email already exists"


class EmailValidationError(BadRequest):
    code = 400
    description = "Email is invalid."


class AbstractPasswordValidationException(BadRequest):
    code = 400
    description = 'This is the parent class'


class PasswordTooShortError(AbstractPasswordValidationException):
    description = "Your password should contain more than 8 characters."


class PasswordCharacterCaseError(AbstractPasswordValidationException):
    description = "Your password should contain at least one capital letter."


class PasswordDigitError(AbstractPasswordValidationException):
    description = "Your password should contain at least one number."


class PasswordSpecialCharacterError(AbstractPasswordValidationException):
    description = "Your password should contain at least one special character."


# HTTP Error Handler
class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        
from werkzeug.exceptions import BadRequest


class EmailExistsError(BadRequest):
    code = 400
    description = "A user with that email already exists"


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
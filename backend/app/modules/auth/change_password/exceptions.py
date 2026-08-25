class EmptyOldPasswordException(Exception):
    pass
class EmptyNewPasswordException(Exception):
    pass
class PasswordUnchangedException(Exception):
    pass
class UserNotFoundException(Exception):
    pass
class WrongOldPasswordException(Exception):
    pass
class UserNotFoundException(Exception):
    pass
class WrongPasswordException(Exception):
    pass
class InvalidPhoneNumberException(Exception):
    pass
class EmptyPasswordException(Exception):
    pass
class UserLockedException(Exception):
    pass
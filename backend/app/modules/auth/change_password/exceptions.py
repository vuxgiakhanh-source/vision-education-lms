class EmptyNewPasswordException(Exception):
    pass
class PasswordUnchangedException(Exception):
    pass
class UserNotFoundException(Exception):
    pass

class UserLockedException(Exception):
    pass

class UserNotFoundException(Exception):
    pass
class WrongPasswordException(Exception):
    def __init__(self, user_id: int | None = None):
        super().__init__(user_id)
        self.user_id = user_id
class InvalidPhoneNumberException(Exception):
    pass
class EmptyPasswordException(Exception):
    pass
class UserLockedException(Exception):
    pass


class TooManyLoginAttemptsException(Exception):
    def __init__(self, retry_after_seconds: int):
        super().__init__(retry_after_seconds)
        self.retry_after_seconds = retry_after_seconds

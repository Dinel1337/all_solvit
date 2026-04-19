from enum import Enum

class ErrorUser(Enum):
    USER_NOT_FOUND = 'USER-404'
    USER_NOT_CREATED = 'USER-400'
    USER_EMAIL_EXIST = 'USER-409'
    USER_ERROR_VALIDATION = "USER_NOT_VALID-409"
    USER_BAD_PARAMETR = 'USER-400'

class ErrorEmail(Enum):
    INVALID_EMAIL = 'EMAIL-001'
    TYPE_ERROR_EMAIL = 'EMAIL-002'
    VALIDATION_ERROR = 'EMAIL-003'

__all__ = ['ErrorUser', 'ErrorEmail']
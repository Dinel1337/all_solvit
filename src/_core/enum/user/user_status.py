from enum import Enum

class OperationUserStatus(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    
class ServerStatus(Enum):
    INTERVAL_ERROR = 'INTERVAL_ERROR'


__all__ = ['OperationUserStatus', 'ServerStatus']
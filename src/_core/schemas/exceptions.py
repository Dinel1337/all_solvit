from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict = {}
    
class ErrorResponseBetter(BaseModel):
    """Ответ при ошибке"""
    detail: str
    status: int
    code: str

from fastapi import FastAPI

from .handler import app_exception_handler, general_exception_handler, not_found_exception_handler
from ..exceptions import AppException, NotFoundError

def setup_exception_handlers(app: FastAPI) -> None:
    """Регистрирует ошибку, которая наследуется от AppException"""

    app.add_exception_handler(NotFoundError, not_found_exception_handler)
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    print("✅ Handlers registered")

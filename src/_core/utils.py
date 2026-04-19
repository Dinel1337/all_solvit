import os
import bcrypt
import types
import inspect
import subprocess

from pydantic import BaseModel
from .database import database_construct
from functools import wraps
from typing import Optional, Any, List, Tuple, TypeVar, Any, Dict, Callable, Type
from .exceptions.main_error import NotFoundError, AppException

T = TypeVar('T', bound=BaseModel)

tab = lambda : print('\n\n') 
cls = lambda : os.system('clear') # как на винде

def formater_console(func):
    """ Форматирует консоль под открытые задачи """
    def wrapper(*argv, **kwargs):
        cls()
        tab()
        try:
            result = func(*argv, **kwargs)
        finally:
            for _ in range(1):
                tab()
        
        return result
    return wrapper

def free_port(port: int):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                result = subprocess.run(
                    f"lsof -ti:{port} | xargs kill -9",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"Порт {port} освобождён")
                else:
                    print(f"Не удалось освободить порт {port}: {result.stderr}")
            except Exception as e:
                print(f"Ошибка при освобождении порта: {e}")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def crypt_pass(password: str) -> str:
    """Хеширование пароля"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    return password_hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def with_db(db_path: str):
    """
    Декоратор, который добавляет зависимость БД к функции
    
    Использование:
        @with_db('app.db')
        async def get_db_sqlite():
            yield db
    """
    def decorator(func):
        @wraps(func)
        async def wrapper():
            db = database_construct(db_path)
            try:
                async for result in func(db):
                    yield result
            finally:
                if hasattr(db, 'close'):
                    await db.close()
        return wrapper
    return decorator


def auto_all():
    """Автоматический __all__ для __init__.py"""
    frame = inspect.currentframe().f_back
    module = inspect.getmodule(frame)
    
    return [
        name for name, obj in module.__dict__.items()
        if not name.startswith('_') 
        and not isinstance(obj, types.ModuleType)
    ]

class StringNormalizer:
    """Класс-нормализатор с явными методами"""
    
    @staticmethod
    def strings(*args: Any) -> Tuple[Any, ...]:
        """Нормализация отдельных аргументов"""
        return tuple(
            arg.lower().strip() if isinstance(arg, str) else arg
            for arg in args
        )
    
    @staticmethod
    def model(model: T, fields: Optional[List[str]] = None) -> T:
        """Нормализация Pydantic модели"""
        normalized_data = {}
        for field_name, value in model.dict().items():
            if fields is None or field_name in fields:
                if isinstance(value, str):
                    normalized_data[field_name] = value.lower().strip()
                else:
                    normalized_data[field_name] = value
            else:
                normalized_data[field_name] = value
        return model.__class__(**normalized_data)
    
    @staticmethod
    def dict(data: dict, fields: Optional[List[str]] = None) -> dict:
        """Нормализация словаря"""
        result = {}
        for key, value in data.items():
            if fields is None or key in fields:
                if isinstance(value, str):
                    result[key] = value.lower().strip()
                else:
                    result[key] = value
            else:
                result[key] = value
        return result







class RaiseControl:
    """
    Универсальный декоратор для обработки исключений в асинхронных репозиториях.
    
    Автоматически определяет позицию search_param, наличие self и выбирает нужный класс ошибки
    на основе переданного ключа или модели SQLAlchemy.
    
    Parameters
    ----------
    error_map : Dict
        Маппинг строковых ключей на классы исключений.
        Пример: {"exercise": ExerciseNotFoundError, "category": CategoryNotFoundError}
    
    model_error_map : Dict
        Маппинг SQLAlchemy моделей на классы исключений.
        Пример: {Exercise: ExerciseNotFoundError, Category: CategoryNotFoundError}
    
    default_error : Type[Exception], optional
        Исключение по умолчанию, если не найден подходящий класс в маппингах.
        По умолчанию: NotFoundError
    
    Examples
    --------
    Инициализация:
    
    >>> _error_map = {"exercise": ExerciseNotFoundError, "category": CategoryNotFoundError}
    >>> _model_error_map = {Exercise: ExerciseNotFoundError, Category: CategoryNotFoundError}
    >>> rc = RaiseControl(_error_map, _model_error_map, default_error=NotFoundError)
    
    Базовое использование:
    
    >>> @rc(exc='exercise')
    ... async def get_by_id(self, id: int):
    ...     return await session.get(Exercise, id)
    
    С явным указанием позиции модели:
    
    >>> @rc(exc='exercise', model_pos=2)
    ... async def get_by_name(self, name: str, model: Any = None):
    ...     return await repository.find_by(name=name)
    
    Только проверка на None без указания типа ошибки:
    
    >>> @rc(search_field='description')
    ... async def find_by_pattern(self, pattern: str):
    ...     return await session.execute(query)
    
    Notes
    -----
    - Декоратор работает только с асинхронными функциями (async def)
    - При result = None и handle_none=True (по умолчанию) выбрасывается исключение
    - search_param определяется автоматически: берётся первый не-self аргумент
    - Если нужно обрабатывать исключения из самого метода, включите handle_exception=True
    """
    def __init__(self, error_map: Dict, model_error_map: Dict = None, default_error: Type[Exception] = NotFoundError):
        self.error_map = error_map
        self.model_error_map = model_error_map
        self.default_error = default_error
    
    def __call__(self, 
                 exc: Optional[str] = None,
                 search_param: Any = None,
                 search_field: Optional[str] = None,
                 param_pos: int = -1,
                 model_pos: Optional[int] = None,
                 handle_none: bool = True,
                 handle_exception: bool = False,
                 main_except: bool = False,
                 error_message: Optional[str] = None,
                 error_code: Optional[str] = None) -> Callable:
        
        return self._make_decorator(
            exc, search_param, search_field, param_pos, model_pos,
            handle_none, handle_exception, main_except, error_message, error_code
        )
    
    def _make_decorator(self, exc, search_param, search_field,
                        param_pos, model_pos,
                        handle_none, handle_exception, main_except,
                        error_message, error_code):
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    result = await func(*args, **kwargs)
                    
                    if handle_none and result is None:
                        param = search_param if search_param is not None else self._get_param(args, param_pos)
                        
                        ErrorClass = self._get_error_class(args, model_pos, exc)
                        raise (ErrorClass or self.default_error)(
                            search_param=param,
                            search_field=search_field,
                            message=error_message,
                            details={"error_code": error_code} if error_code else None
                        )
                    return result
                    
                except Exception as e:
                    if main_except or handle_exception:
                        param = search_param if search_param is not None else self._get_param(args, param_pos)
                        
                        ErrorClass = self._get_error_class(args, model_pos, exc)
                        raise (ErrorClass or self.default_error)(
                            search_param=param,
                            search_field=search_field,
                            message=error_message or str(e),
                            details={"original_error": str(e), "error_code": error_code}
                        ) from e
                    raise
            return wrapper
        return decorator
    
    def _get_param(self, args: tuple, param_pos: int) -> Any:
        """Автоматически определяет позицию параметра"""
        if param_pos >= 0:
            return args[param_pos] if len(args) > param_pos else None
        
        if len(args) == 2:
            return args[1]
        if len(args) > 2:
            return args[-1]
        return None
    
    def _get_error_class(self, args: tuple, model_pos: Optional[int], exc: Optional[str]):
        ErrorClass = None
        if exc is not None:
            ErrorClass = self.error_map.get(exc)
        
        if ErrorClass is None and model_pos is not None and len(args) > model_pos:
            model = args[model_pos]
            if isinstance(model, type) and hasattr(model, '__bases__'):
                ErrorClass = self.model_error_map.get(model)
        
        return ErrorClass

# def get_all_exports():
#     """Автоматически собирает все публичные имена"""
#     return [name for name in dir() if not name.startswith('_')]

# def auto_import_classes_from_files(path: Path, package_name: str, exclude: List[str] = None) -> List[str]:
#     """
#     Автоматический импорт классов, исключая указанные
#     """
#     exclude = exclude or []
#     __all__ = []
    
#     for file in path.glob('*.py'):
#         if file.name == "__init__.py":
#             continue
        
#         module_name = file.stem
        
#         try:
#             module = importlib.import_module(f".{module_name}", package=package_name)
            
#             for attr_name in dir(module):
#                 if attr_name.startswith('_'):
#                     continue
                
#                 if attr_name in exclude:
#                     continue
                
#                 obj = getattr(module, attr_name)
                
#                 if isinstance(obj, type):
#                     module_of_obj = getattr(obj, '__module__', '')
#                     if module_of_obj == module.__name__:
#                         globals()[attr_name] = obj
#                         __all__.append(attr_name)
                        
#         except Exception as e:
#             print(f"Ошибка импорта {module_name}: {e}")
    
#     return __all__
from pydantic import BaseModel, ConfigDict, constr, field_validator, Field
from ..enum import OperationUserStatus
from typing import Annotated
from ..models import validate_email_address, password_length_check
from fastapi import Query
import re

PasswordStr = Annotated[
    str,
    constr(min_length=6, max_length=32, pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).*$")
]

USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50
USERNAME_PATTERN = r"^[a-zA-Z0-9_]+$"
USERNAME_PATTERN_ERROR = "Username can only contain letters, numbers, and underscores"

class CodeResponse(BaseModel):
    """Схема для кода подтверждения"""
    code: int

class UserBase(BaseModel):
    """Базовая схема пользователя с email и username"""
    email: str
    username: str = Field(
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
        pattern=USERNAME_PATTERN,
        examples=["john_doe", "johndoe123"]
    )

    @field_validator('email')
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip()
        return validate_email_address(value)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, value: str) -> str:
        """Полная валидация username"""
        value = value.strip()
        
        if len(value) < USERNAME_MIN_LENGTH:
            raise ValueError(f'Username must be at least {USERNAME_MIN_LENGTH} characters')
        if len(value) > USERNAME_MAX_LENGTH:
            raise ValueError(f'Username must be at most {USERNAME_MAX_LENGTH} characters')
        
        if not re.match(USERNAME_PATTERN, value):
            raise ValueError(USERNAME_PATTERN_ERROR)
        
        reserved_usernames = [
            'admin', 'administrator', 'root', 'system', 'user', 
            'test', 'guest', 'api', 'support', 'info'
        ]
        if value.lower() in reserved_usernames:
            raise ValueError(f'Username "{value}" is reserved and cannot be used')
        
        if value.isdigit():
            raise ValueError('Username cannot contain only numbers')
        
        if value.startswith('_') or value.endswith('_'):
            raise ValueError('Username cannot start or end with underscore')
        
        if '__' in value:
            raise ValueError('Username cannot contain consecutive underscores')
        
        return value.lower()

class UserCreate(UserBase):
    """Схема для создания пользователя (регистрация)"""
    password: PasswordStr
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@gmail.com",
                    "username": "john_doe",
                    "password": "Dinelefox123"
                }
            ]
        }
    }

    @field_validator('password')
    @classmethod
    def password_length(cls, v: str):
        v = v.strip()
        return password_length_check(v)

class UserInDB(UserBase):
    """Схема пользователя из БД"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    status_operation: OperationUserStatus | None = OperationUserStatus.CREATED

class UserDelete(BaseModel):
    """Схема для удаления пользователя"""
    model_config = ConfigDict(from_attributes=True)
    id: int

class CheckUser(BaseModel):
    """Схема для проверки существования пользователя"""
    username: str | None = Query(None, description="Логин пользователя")
    email: str | None = Query(None, description="Email пользователя")
    token: str | None = Query(None, description="token пользователя")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_email_address(value)
    
    @field_validator('username')
    @classmethod
    def validate_username_query(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if len(value) < USERNAME_MIN_LENGTH:
            raise ValueError(f'Username must be at least {USERNAME_MIN_LENGTH} characters')
        if len(value) > USERNAME_MAX_LENGTH:
            raise ValueError(f'Username must be at most {USERNAME_MAX_LENGTH} characters')
        if not re.match(USERNAME_PATTERN, value):
            raise ValueError(USERNAME_PATTERN_ERROR)
        return value

class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    username: str
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "john_doe",
                    "password": "Dinelefox123"
                }
            ]
        }
    }
    
    @field_validator('username')
    @classmethod
    def validate_username_login(cls, value: str) -> str:
        value = value.strip()
        if len(value) < USERNAME_MIN_LENGTH:
            raise ValueError(f'Username must be at least {USERNAME_MIN_LENGTH} characters')
        if len(value) > USERNAME_MAX_LENGTH:
            raise ValueError(f'Username must be at most {USERNAME_MAX_LENGTH} characters')
        if not re.match(USERNAME_PATTERN, value):
            raise ValueError(USERNAME_PATTERN_ERROR)
        return value.lower()

class UserLoginResponse(BaseModel):
    """Схема ответа при успешном входе"""
    id: int
    username: str
    email: str
    token: str
    token_type: str = "bearer"
    expires_in: int

class UserCreateResponse(BaseModel):
    """Схема ответа при успешной регистрации"""
    id: int
    username: str
    email: str
"""Сервисный слой с логгированием.

Компоненты:
- LoggerService — базовый класс с цветным логгером (INFO при DEBUG, иначе ERROR)
- UserService — бизнес-логика пользователей (создание, аутентификация, токены)

Цвета уровней:
- DEBUG — серый
- INFO — зелёный
- WARNING — жёлтый
- ERROR — красный
"""
from .BaseServise import LoggerService
from .user_service import UserService
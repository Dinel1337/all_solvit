from src._core.schemas import StripStringsModel
from pydantic import HttpUrl
# Схема для тела запроса
class DomainCreate(StripStringsModel):
    url: HttpUrl
    name: str | None = None

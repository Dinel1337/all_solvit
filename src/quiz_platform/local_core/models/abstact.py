from src._core.database import QuizPlatformBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String

class BaseModel(QuizPlatformBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class NamedModel(BaseModel):
    __abstract__ = True
    name: Mapped[str] = mapped_column(String(256), nullable=False)
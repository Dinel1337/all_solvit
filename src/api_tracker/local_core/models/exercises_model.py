from sqlalchemy import Integer, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, relationship, mapped_column
from src._core.database import ApiTrackerBase
from typing import Optional

class Exercise(ApiTrackerBase):
    __tablename__ = 'exercises'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    category_id: Mapped[int] = mapped_column(
        ForeignKey('api_tracker.categories.id', ondelete='RESTRICT'),  # ← явно указана схема
        index=True
    )
    muscle_group_id: Mapped[int] = mapped_column(
        ForeignKey('api_tracker.muscle_groups.id', ondelete='RESTRICT'),  # ← явно указана схема
        index=True
    )
    
    category: Mapped["Category"] = relationship(
        back_populates='exercises',
        lazy='selectin'
    )
    muscle_group: Mapped["MuscleGroup"] = relationship(
        back_populates='exercises',
        lazy='selectin'
    )
        
    def __repr__(self) -> str:
        return f"<Упражнение(id={self.id}, name='{self.name}')>"


class Category(ApiTrackerBase):
    __tablename__ = 'categories'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates='category',
        lazy='selectin',
        cascade='save-update, merge'
    )
    
    def __repr__(self) -> str:
        return f"<Категория(id={self.id}, name='{self.name}')>"


class MuscleGroup(ApiTrackerBase):
    __tablename__ = 'muscle_groups'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates='muscle_group',
        lazy='selectin',
        cascade='save-update, merge'
    )
    
    def __repr__(self) -> str:
        return f"<ГруппаМышц(id={self.id}, name='{self.name}')>"
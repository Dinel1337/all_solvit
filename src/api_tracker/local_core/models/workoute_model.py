from sqlalchemy import Integer, String, ForeignKey, Text, SmallInteger, DateTime
from sqlalchemy.orm import Mapped, relationship, mapped_column
from src._core.database import ApiTrackerBase
from .exercises_model import Exercise
from datetime import datetime
from src._core.models import User

class Workout(ApiTrackerBase):
    """Модель тренировки."""
    __tablename__ = 'workouts'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('public.users.id', ondelete='RESTRICT'))
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    exercises: Mapped[list["WorkoutExercise"]] = relationship(back_populates='workout', cascade="all, delete-orphan")
    user: Mapped[User] = relationship(lazy='selectin')

    def __repr__(self) -> str:
        return f"<Workout(id={self.id}, name='{self.name}')>"

class WorkoutExercise(ApiTrackerBase):
    """Связь тренировки с упражнениями."""
    __tablename__ = 'workout_exercises'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey('api_tracker.workouts.id', ondelete="CASCADE"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey('api_tracker.exercises.id'))
    sets: Mapped[int] = mapped_column(SmallInteger)
    reps: Mapped[int] = mapped_column(SmallInteger)
    weight: Mapped[float] = mapped_column(nullable=True)    
    order: Mapped[int] = mapped_column(SmallInteger)
    
    workout: Mapped["Workout"] = relationship(back_populates='exercises')
    exercise: Mapped["Exercise"] = relationship(lazy='selectin')
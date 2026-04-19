from __future__ import annotations

from sqlalchemy import Text, Boolean, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src._core.models import User

from datetime import datetime
from .abstact import NamedModel, BaseModel
from ..schemas import QuizResponse, QuestionResponse, AnswerOptionResponse
from typing import Optional, List

class Quiz(NamedModel):
    __tablename__ = 'quiz'
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("public.users.id"))
    status: Mapped[str] = mapped_column(String(20), default="draft")
    unique_link: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    
    author: Mapped[User] = relationship(lazy='selectin') 
    questions: Mapped[List["Question"]] = relationship(back_populates="quiz", cascade="all, delete-orphan")
    
    # @property
    def to_dict(self) -> dict:
        return QuizResponse(
            id=self.id,
            name=self.name,
            description=self.description,
            status=self.status,
            author_id=self.author_id,
            questions=[
                QuestionResponse(
                    id=q.id,
                    text=q.text,
                    points=q.points,
                    order=q.order,
                    options=[
                        AnswerOptionResponse(
                            id=opt.id,
                            text=opt.text,
                            is_correct=opt.is_correct
                        )
                        for opt in q.options
                    ]
                )
                for q in self.questions
            ]
        ).model_dump(exclude_none=True)
        
    def __repr__(self) -> str:
        return f"<Quiz(id={self.id}, name='{self.name}')>"

class Question(BaseModel):
    __tablename__ = 'question'
    
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quiz_platform.quiz.id"))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=1)
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    quiz: Mapped["Quiz"] = relationship(back_populates="questions")
    options: Mapped[List["AnswerOption"]] = relationship(
        back_populates="question", 
        cascade="all, delete-orphan",
        lazy='selectin')
    user_answers: Mapped[List["UserAnswer"]] = relationship(back_populates="question")
    
    def __repr__(self) -> str:
        return f"<Question(id={self.id}, text='{self.text[:50]}')>"


class AnswerOption(BaseModel):
    __tablename__ = 'answer_option'
    
    question_id: Mapped[int] = mapped_column(ForeignKey("quiz_platform.question.id"))
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    
    question: Mapped["Question"] = relationship(back_populates="options")
    user_answers: Mapped[List["UserAnswer"]] = relationship(
            back_populates="selected_option",
            lazy='selectin'  # ← если нужно
        )    
    def __repr__(self) -> str:
        return f"<AnswerOption(id={self.id}, text='{self.text[:30]}', correct={self.is_correct})>"


class Attempt(BaseModel):
    __tablename__ = 'attempt'
    
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quiz_platform.quiz.id"))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("public.users.id"), nullable=True)
    anonymous_token: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    started_at: Mapped[datetime] = mapped_column(default=datetime.now)
    finished_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    total_score: Mapped[int] = mapped_column(Integer, default=0)
    
    quiz: Mapped["Quiz"] = relationship()
    user: Mapped[Optional[User]] = relationship()
    user_answers: Mapped[List["UserAnswer"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")


class UserAnswer(BaseModel):
    __tablename__ = 'user_answer'
    
    attempt_id: Mapped[int] = mapped_column(ForeignKey("quiz_platform.attempt.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("quiz_platform.question.id"))
    selected_option_id: Mapped[int] = mapped_column(ForeignKey("quiz_platform.answer_option.id"))
    
    attempt: Mapped["Attempt"] = relationship(back_populates="user_answers")
    question: Mapped["Question"] = relationship(back_populates="user_answers")
    selected_option: Mapped["AnswerOption"] = relationship(back_populates="user_answers")
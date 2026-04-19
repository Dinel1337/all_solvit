from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Type, Literal, Dict, List, Optional

from src._core.repositories.main_repository import BaseRepository
from src._core import RaiseControl
from src._core.exceptions import NotFoundError
from ..schemas import QuestionCreate, QuizCreate, QuizResponse, QuestionResponse, AnswerOptionCreate
from ..exceptions import QuestionNotFoundError, QuizNotFoundError, AnswerOptionNotFoundError
from ..models.quiz_model import Quiz, Question, AnswerOption

_ExcMeta = Literal['quiz', 'question', 'answer_option']

_error_map: Dict[_ExcMeta, Type[NotFoundError]] = {
    "quiz": QuizNotFoundError,
    "question": QuestionNotFoundError,
    "answer_option": AnswerOptionNotFoundError,
}

_model_error_map = {
    Quiz: QuizNotFoundError,
    Question: QuestionNotFoundError,
    AnswerOption: AnswerOptionNotFoundError,
}

RControl = RaiseControl(
    _error_map, 
    _model_error_map, 
    default_error=QuizNotFoundError)

class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(session, Quiz)

    @RControl(exc='quiz', param_pos=1)
    async def get_by_id(self, id: int, simple: bool = False):
        """
        active = True, означает что будут находиться все публикации, иначе только те что имеют status == 'published' 
        """
        if simple:
            return await self.find_one_by(id=id)
        return await self.find_one_by_with_options(
            [selectinload(Quiz.questions).selectinload(Question.options)],
            id=id
        )
    

    @RControl(exc='quiz', param_pos=1)
    async def get_by_name_z(self, name: str, simple: bool = False):
        if simple:
            return await self.find_one_by(name=name)
        return await self.find_one_by_with_options(
            [selectinload(Quiz.questions).selectinload(Question.options)],
            name=name
        )
    
    @RControl(exc='quiz')
    async def get_quizzes(
        self, 
        search: Optional[str] = None, 
        limit: int = 100, 
        offset: int = 0,
        active: bool = False
    ) -> List[Quiz]:
        """Получение списка викторин с поиском по name и description
        
        active = True - возвращает все викторины
        active = False - возвращает только опубликованные (status = 'published')
        """
        stmt = select(Quiz).options(
            selectinload(Quiz.questions).selectinload(Question.options)
        )
    
        if search:
            stmt = stmt.where(
                (Quiz.name.ilike(f"%{search}%")) | 
                (Quiz.description.ilike(f"%{search}%"))
            )
        
        if not active:
            stmt = stmt.where(Quiz.status == 'published')
    
        stmt = stmt.offset(offset).limit(limit).order_by(Quiz.id.desc())
    
        result = await self.session.execute(stmt)
        return result.scalars().all()

    
    @RControl(main_except=True, error_message='Ошибка при добавлении Викторины')
    async def create_quiz(self, data: QuizCreate, user_id):
        quiz = await self.create(
            commit=False,
            data={
                "name": data.name,
                "description": data.description,
                "status": data.status,
                "author_id": user_id
            }
        )

        return await QuestionRepository(self.session).create_question(data.questions, quiz)


class QuestionRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.question = BaseRepository(session, Question)
        self.answer = BaseRepository(session, AnswerOption)
        
    async def create_question(self, data: List[QuestionCreate], quiz: Quiz):
        for question in data:
            q = await self.question.create(
                commit=False,
                data={
                    "quiz_id": quiz.id,
                    "text": question.text,
                    "points": question.points,
                    "order": question.order
                }
            )

            for opt in question.options:
                await self._create_answer_option(q.id, opt)

        await self.session.commit()
        
        stmt = select(Quiz).where(Quiz.id == quiz.id).options(
            selectinload(Quiz.questions).selectinload(Question.options)
        )
        quiz = (await self.session.execute(stmt)).scalar_one()
        return quiz

    # @RControl('answer_option')
    async def _create_answer_option(self, question_id: int, opt: AnswerOptionCreate):
        await self.answer.create(
            commit=False,
            data={
                "question_id": question_id,
                "text": opt.text,
                "is_correct": opt.is_correct
            }
        )
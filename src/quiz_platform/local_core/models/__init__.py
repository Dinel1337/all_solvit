"""SQLAlchemy модели для Quiz Platform.

- Quiz — квиз (name, description, status, author_id)
- Question — вопрос (text, points, order)
- AnswerOption — вариант ответа (text, is_correct)
- Attempt — попытка прохождения (user_id, anonymous_token, score)
- UserAnswer — ответ пользователя (связь attempt/question/option)
"""

from .quiz_model import Quiz, Question, AnswerOption, Attempt, UserAnswer

__all__ = [
    'Quiz',
    'Question',
    'AnswerOption',
    'Attempt',
    'UserAnswer',
]
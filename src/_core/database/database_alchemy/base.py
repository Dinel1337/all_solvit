from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event, text
import logging

logger = logging.getLogger(__name__)

class PublicBase(DeclarativeBase):
    __abstract__ = True   
    __table_args__ = {'schema': 'public'}

class ApiTrackerBase(PublicBase):
    __abstract__ = True     
    __table_args__ = {'schema': 'api_tracker'}

class QuizPlatformBase(PublicBase):
    __abstract__ = True       
    __table_args__ = {'schema': 'quiz_platform'}

def _create_schema_if_not_exists(connection, schema_name):
    """Проверяет существование схемы и создаёт, если её нет"""
    exists = connection.execute(
        text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :schema"),
        {"schema": schema_name}
    ).scalar()
    
    if not exists:
        connection.execute(text(f"CREATE SCHEMA {schema_name}"))
        logger.info(f"Schema '{schema_name}' created")
    else:
        logger.debug(f"Schema '{schema_name}' already exists")

@event.listens_for(PublicBase.metadata, 'before_create')
def create_public_schema(target, connection, **kw):
    _create_schema_if_not_exists(connection, 'public')

@event.listens_for(ApiTrackerBase.metadata, 'before_create')
def create_api_tracker_schema(target, connection, **kw):
    _create_schema_if_not_exists(connection, 'api_tracker')

@event.listens_for(QuizPlatformBase.metadata, 'before_create')
def create_quiz_platform_schema(target, connection, **kw):
    _create_schema_if_not_exists(connection, 'quiz_platform')
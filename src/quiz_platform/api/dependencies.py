"""Зависимости для Quiz Platform.

- get_current_user — извлечение пользователя из JWT токена
"""
from src._core.database import get_db
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src._core.auth.dependencies import token_dispatch

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    return await token_dispatch(request, db)
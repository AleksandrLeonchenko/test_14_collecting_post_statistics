from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from database import get_async_session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """
    Асинхронная функция для получения базы данных пользователей.

    Args:
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.

    Yields:
        SQLAlchemyUserDatabase: Экземпляр базы данных пользователей.

    """
    yield SQLAlchemyUserDatabase(session, User)

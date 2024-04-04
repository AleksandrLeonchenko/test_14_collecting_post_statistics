from typing import Optional

from fastapi import Depends, Request
from fastapi_users import (BaseUserManager, IntegerIDMixin, exceptions, models,
                           schemas)

from auth.models import User
from auth.utils import get_user_db
from config import SECRET_AUTH


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    Менеджер пользователей.

    Attributes:
        reset_password_token_secret (str): Секрет для сброса пароля.
        verification_token_secret (str): Секрет для подтверждения.

    """
    reset_password_token_secret = SECRET_AUTH
    verification_token_secret = SECRET_AUTH

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Вызывается после регистрации пользователя.

        Args:
            user (User): Зарегистрированный пользователь.
            request (Optional[Request], optional): Запрос FastAPI. По умолчанию None.

        """
        print(f"User {user.id} has registered.")

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:
        """
        Создает нового пользователя.

        Args:
            user_create (UserCreate): Данные нового пользователя.
            safe (bool, optional): Флаг безопасного создания. По умолчанию False.
            request (Optional[Request], optional): Запрос FastAPI. По умолчанию None.

        Returns:
            Созданный пользователь.

        Raises:
            exceptions.UserAlreadyExists: Если пользователь уже существует.

        """
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["role_id"] = 1

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


async def get_user_manager(user_db=Depends(get_user_db)):
    """
    Асинхронная функция для получения менеджера пользователей.

    Args:
        user_db: Зависимость для получения базы данных пользователей.

    Yields:
        UserManager: Экземпляр менеджера пользователей.

    """
    yield UserManager(user_db)

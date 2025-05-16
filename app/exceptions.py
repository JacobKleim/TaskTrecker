"""
Модуль кастомных исключений.

Содержит расширенные HTTPException для пользователей и задач,
предназначенные для централизованной обработки ошибок в сервисных слоях.
"""

import logging

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class UserNotFoundException(HTTPException):
    """
    Исключение: пользователь не найден в базе.

    Используется, когда указанный ID пользователя не существует
    или пользователь был удалён.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден. Возможно, он был удалён или ID указан неверно.",
        )


class ForbiddenUserUpdateException(HTTPException):
    """
    Исключение: попытка обновить чужого пользователя.

    Вызывается, если текущий пользователь не совпадает с ID редактируемого.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете обновлять данные других пользователей.",
        )


class ForbiddenUserDeleteException(HTTPException):
    """
    Исключение: попытка удалить другого пользователя.

    Вызывается, если пользователь пытается удалить чужой аккаунт.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Удаление других пользователей запрещено.",
        )


class TaskNotFoundException(HTTPException):
    """
    Исключение: задача не найдена.

    Используется, когда задача отсутствует или не принадлежит текущему пользователю.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена. Убедитесь, что ID указан правильно.",
        )


class ForbiddenTaskUpdateException(HTTPException):
    """
    Исключение: нет прав на редактирование задачи.

    Вызывается, если задача принадлежит другому пользователю.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для редактирования этой задачи.",
        )


class ForbiddenTaskDeleteException(HTTPException):
    """
    Исключение: нет прав на удаление задачи.

    Вызывается, если задача принадлежит другому пользователю.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете удалить задачу, которой не владеете.",
        )

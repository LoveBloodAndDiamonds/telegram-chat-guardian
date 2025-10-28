"""
Конфигурационные данные и настройка логирования.
"""

__all__ = ["Configuration"]

from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()  # Если работаем вне докер-контейнера


@dataclass(frozen=True)
class Configuration:
    """Класс конфигурации всего приложения."""

    bot_token: str = getenv("BOT_TOKEN", "")
    """Токен бота."""

    chat_id: int = int(getenv("CHAT_ID", ""))
    """Айди чата."""

    banwords: tuple[str, ...] = tuple(
        # Преобразуем строку окружения в кортеж уникальных слов в нижнем регистре
        word.strip().lower()
        for word in getenv("BANWORDS", "").split(",")
        if word.strip()
    )
    """Кортеж запрещенных слов, приведенных к нижнему регистру."""

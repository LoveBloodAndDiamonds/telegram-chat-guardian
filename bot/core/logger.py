"""
Настройки логирования.
"""

__all__ = [
    "logger",
    "get_logger",
]

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from loguru import logger

if TYPE_CHECKING:
    from loguru import Logger


class LoggerFactory:
    """Фабрика для создания и кэширования логгеров."""

    # Удаление стандартных обработчиков loguru
    logger.remove()

    # Определение времени хранения для каждого уровня
    _retentions: dict[str, str] = {
        "ERROR": "1 month",
        "INFO": "1 week",
        "DEBUG": "1 day",
        "TRACE": "3 hours",
    }

    # Хранилище логгеров
    _loggers: dict[str, "Logger"] = {}

    @classmethod
    def get_logger(
        cls,
        name: str = "",
        base_dir: str = "logs",
        stdout_level: Literal["ERROR", "INFO", "DEBUG", "TRACE"] = "INFO",
        file_levels: list[Literal["ERROR", "INFO", "DEBUG", "TRACE"]] | None = None,
        enqueue: bool = False,
    ) -> "Logger":
        """Возвращает существующий логгер или создает новый."""
        if name in cls._loggers:
            return cls._loggers[name]  # Возврат кэшированного логгера

        log_path = Path(base_dir) / name
        log_path.mkdir(parents=True, exist_ok=True)

        log = logger.bind(name=name)

        # Логирование в консоль
        log.add(
            sys.stderr,
            level=stdout_level,
            filter=lambda record: name == record["extra"].get("name"),
            format=(
                "<white>{time: %d.%m %H:%M:%S}</white>|"
                "<level>{level}</level>|"
                "{extra[name]}|"
                "<bold>{message}</bold>"
            )
            if name
            else (
                "<white>{time: %d.%m %H:%M:%S}</white>|"
                "<level>{level}</level>|"
                "<bold>{message}</bold>"
            ),
        )

        # Логирование в файлы для разных уровней
        for level in file_levels or ["ERROR", "INFO", "DEBUG"]:
            log.add(
                sink=log_path / f"{level.lower()}.log",  # Путь к файлу логов
                filter=lambda record: name == record["extra"].get("name"),
                level=level,
                format=(
                    "<white>{time: %d.%m %H:%M:%S.%f}</white> | "
                    "<level>{level}</level>| "
                    "{extra[name]}|"
                    "{name} {function} line:{line}| "
                    "<bold>{message}</bold>"
                )
                if name
                else (
                    "<white>{time: %d.%m %H:%M:%S.%f}</white> | "
                    "<level>{level}</level>| "
                    "{name} {function} line:{line}| "
                    "<bold>{message}</bold>"
                ),
                retention=cls._retentions.get(level, "1 week"),
                rotation="10 MB",
                compression="zip",
                encoding="utf-8",
                enqueue=enqueue,
            )

        cls._loggers[name] = log  # Кэширование логгера
        return log


get_logger = LoggerFactory.get_logger  # Сокращение для удобства

logger = get_logger()  # Базовый логгер

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Final

from loguru import logger

from clive.config import LAUNCH_TIME, ROOT_DIRECTORY, settings

LOG_FORMAT: Final[str] = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
    " | <level>{level.icon} {level: <8}</level>"
    " | <WHITE><cyan>{name}</cyan>:<blue>{function}</blue>:<b><green>{line}</green></b></WHITE>"
    " - <level>{message}</level>"
)


def create_log_file(log_name: str, log_group: str | None = None) -> Path:
    log_directory = ROOT_DIRECTORY.parent / "logs" / log_group if log_group else ROOT_DIRECTORY.parent / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)

    log_file_name = f"{LAUNCH_TIME.strftime('%Y-%m-%d_%H-%M-%S')}_{log_name}.log"
    log_file_path = log_directory / log_file_name
    with open(log_file_path, "a", encoding="utf-8"):
        # We just need to create an empty file to which we will log later
        pass

    return log_file_path


LOG_FILE_PATH: Final[Path] = create_log_file(log_name="defined", log_group=settings.LOG_LEVEL.lower())
LOG_FILE_PATH_DEBUG: Final[Path] = create_log_file(log_name="debug", log_group="debug")


def configure_logger() -> None:
    def make_filter(*, level: int | str, level_3rd_party: int | str) -> Callable[..., bool]:
        level_no = getattr(logging, level) if isinstance(level, str) else level
        level_no_3rd_party = getattr(logging, level_3rd_party) if isinstance(level_3rd_party, str) else level_3rd_party

        def __filter(record: dict[str, Any]) -> bool:
            is_3rd_party = ROOT_DIRECTORY not in Path(record["file"].path).parents
            if level_no_3rd_party is not None and is_3rd_party:
                return bool(record["level"].no >= level_no_3rd_party)
            return bool(record["level"].no >= level_no)

        return __filter

    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.DEBUG)

    # Remove all log handlers and propagate everything to root logger
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
        logging.getLogger(name).setLevel(logging.DEBUG)

    logger.remove()
    logger.add(
        sink=LOG_FILE_PATH,
        format=LOG_FORMAT,
        filter=make_filter(level=settings.LOG_LEVEL, level_3rd_party=settings.LOG_LEVEL_3RD_PARTY),
    )
    logger.add(
        sink=LOG_FILE_PATH_DEBUG,
        format=LOG_FORMAT,
        filter=make_filter(level=logging.DEBUG, level_3rd_party=logging.DEBUG),
    )


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type: ignore

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

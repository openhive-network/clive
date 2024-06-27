from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from loguru._simple_sinks import StreamSink

from clive.__private.cli.completion import is_tab_completion_active

if not is_tab_completion_active():
    from loguru import logger as loguru_logger
    from textual import log as textual_logger

    from clive.__private.config import LAUNCH_TIME, ROOT_DIRECTORY, settings

if TYPE_CHECKING:
    from collections.abc import Callable

    from loguru._logger import Core

LOG_FORMAT: Final[str] = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
    " | <level>{level.icon} {level: <8}</level>"
    " | <WHITE><cyan>{name}</cyan>:<blue>{function}</blue>:<b><green>{line}</green></b></WHITE>"
    " - <level>{message}</level>"
)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type: ignore[assignment]

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        loguru_logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class Logger:
    """Logger used to log into both Textual (textual console) and Loguru (file located in logs/)."""

    AVAILABLE_LOG_LEVELS: Final[list[str]] = [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
    ]

    def __init__(self) -> None:
        self.__enabled_loguru = True
        self.__enabled_textual = True

    def __getattr__(self, item: str) -> Callable[..., None]:
        patched = loguru_logger.opt(depth=1)
        loguru_attr = getattr(patched, item, None)
        textual_log_attr = getattr(textual_logger, item, None)

        if not callable(loguru_attr) or not callable(textual_log_attr):
            raise TypeError(
                f"Callable `{item}` not found in either Textual or Loguru loggers.\n"
                f"Try one of: {self.AVAILABLE_LOG_LEVELS}"
            )

        def _hooked(*args: Any, **kwargs: Any) -> None:
            if self.__enabled_loguru:
                loguru_attr(*args, **kwargs)
            if self.__enabled_textual:
                textual_log_attr(*args, **kwargs)

        return _hooked

    def setup(
        self, *, enable_loguru: bool = True, enable_textual: bool = True, enable_stream_handlers: bool = False
    ) -> None:
        self.__enabled_loguru = enable_loguru
        self.__enabled_textual = enable_textual

        if enable_loguru:
            self._configure_loguru(enable_stream_handlers=enable_stream_handlers)

    def _configure_loguru(self, *, enable_stream_handlers: bool = False) -> None:
        dated_log_path_defined, latest_log_path_defined = self._create_dated_and_latest_log_files(
            log_name="defined", log_group=settings.LOG_LEVEL.lower()
        )
        dated_log_path_debug, latest_log_path_debug = self._create_dated_and_latest_log_files(
            log_name="debug", log_group="debug"
        )

        logging.root.handlers = [InterceptHandler()]
        logging.root.setLevel(logging.DEBUG)

        # Remove all log handlers and propagate everything to root logger
        for name in logging.root.manager.loggerDict:
            logging.getLogger(name).handlers = []
            logging.getLogger(name).propagate = True
            logging.getLogger(name).setLevel(logging.DEBUG)

        if not enable_stream_handlers:
            self._remove_stream_handlers()

        loguru_logger.add(
            sink=dated_log_path_defined,
            format=LOG_FORMAT,
            filter=self._make_filter(level=settings.LOG_LEVEL, level_3rd_party=settings.LOG_LEVEL_3RD_PARTY),
        )
        loguru_logger.add(
            sink=latest_log_path_defined,
            format=LOG_FORMAT,
            filter=self._make_filter(level=settings.LOG_LEVEL, level_3rd_party=settings.LOG_LEVEL_3RD_PARTY),
        )
        loguru_logger.add(
            sink=dated_log_path_debug,
            format=LOG_FORMAT,
            filter=self._make_filter(level=logging.DEBUG, level_3rd_party=logging.DEBUG),
        )
        loguru_logger.add(
            sink=latest_log_path_debug,
            format=LOG_FORMAT,
            filter=self._make_filter(level=logging.DEBUG, level_3rd_party=logging.DEBUG),
        )

    def _create_dated_and_latest_log_files(self, log_name: str, log_group: str | None = None) -> tuple[Path, Path]:
        def create_empty_file(file_name: str) -> Path:
            empty_file_path = log_directory / file_name
            with empty_file_path.open("w", encoding="utf-8"):
                """We just need to create an empty file to which we will log later"""
            return empty_file_path

        log_directory = Path(settings.log_path)
        if log_group:
            log_directory = log_directory / log_group
        log_directory.mkdir(parents=True, exist_ok=True)

        dated_log_file_name = f"{LAUNCH_TIME.strftime('%Y-%m-%d_%H-%M-%S')}_{log_name}.log"
        dated_log_path = create_empty_file(dated_log_file_name)

        latest_log_file_name = "latest.log"
        latest_log_path = create_empty_file(latest_log_file_name)

        return dated_log_path, latest_log_path

    def _make_filter(self, *, level: int | str, level_3rd_party: int | str) -> Callable[..., bool]:
        level_no = getattr(logging, level) if isinstance(level, str) else level
        level_no_3rd_party = getattr(logging, level_3rd_party) if isinstance(level_3rd_party, str) else level_3rd_party

        def _filter(record: dict[str, Any]) -> bool:
            is_3rd_party = ROOT_DIRECTORY not in Path(record["file"].path).parents
            if level_no_3rd_party is not None and is_3rd_party:
                return bool(record["level"].no >= level_no_3rd_party)
            return bool(record["level"].no >= level_no)

        return _filter

    def _remove_stream_handlers(self) -> None:
        """Remove all handlers that log to stdout and stderr."""
        core: Core = loguru_logger._core  # type: ignore[attr-defined]
        for handler in core.handlers.values():
            if isinstance(handler._sink, StreamSink):
                loguru_logger.remove(handler._id)


logger = Logger()

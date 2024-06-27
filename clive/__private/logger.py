from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from loguru._simple_sinks import StreamSink

from clive.__private.cli.completion import is_tab_completion_active

if not is_tab_completion_active():
    from loguru import logger as loguru_logger
    from textual import log as textual_logger

    from clive.__private.config import LAUNCH_TIME, ROOT_DIRECTORY

if TYPE_CHECKING:
    from collections.abc import Callable

    from loguru._logger import Core

    from clive.__private.safe_settings import SafeSettings

LogFilePaths = tuple[Path, ...]
GroupLogFilePaths = dict[str, LogFilePaths]

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
                f"Try one of: {self.safe_settings_delayed.AVAILABLE_LOG_LEVELS}"
            )

        def _hooked(*args: Any, **kwargs: Any) -> None:
            if self.__enabled_loguru:
                loguru_attr(*args, **kwargs)
            if self.__enabled_textual:
                textual_log_attr(*args, **kwargs)

        return _hooked

    @property
    def safe_settings_delayed(self) -> SafeSettings:
        from clive.__private.safe_settings import safe_settings

        return safe_settings

    def setup(
        self, *, enable_loguru: bool = True, enable_textual: bool = True, enable_stream_handlers: bool = False
    ) -> None:
        self.__enabled_loguru = enable_loguru
        self.__enabled_textual = enable_textual

        if enable_loguru:
            self._configure_loguru(enable_stream_handlers=enable_stream_handlers)

    def _configure_loguru(self, *, enable_stream_handlers: bool = False) -> None:
        log_paths = self._create_log_files()

        logging.root.handlers = [InterceptHandler()]
        logging.root.setLevel(logging.DEBUG)

        # Remove all log handlers and propagate everything to root logger
        for name in logging.root.manager.loggerDict:
            logging.getLogger(name).handlers = []
            logging.getLogger(name).propagate = True
            logging.getLogger(name).setLevel(logging.DEBUG)

        if not enable_stream_handlers:
            self._remove_stream_handlers()

        self._add_file_handlers(log_paths)

    def _create_log_files(self) -> GroupLogFilePaths:
        log_paths: GroupLogFilePaths = {}
        log_levels = self.safe_settings_delayed.log_levels
        for log_level in log_levels:
            log_level_lower = log_level.lower()
            log_level_upper = log_level.upper()

            available_log_levels = self.safe_settings_delayed.AVAILABLE_LOG_LEVELS
            if log_level_upper not in available_log_levels:
                raise RuntimeError(f"Invalid log level: {log_level}, expected one of {available_log_levels}.")

            log_paths[log_level_upper] = self._create_log_files_per_group(group_name=log_level_lower)
        return log_paths

    def _create_log_files_per_group(self, group_name: str) -> LogFilePaths:
        def create_empty_file(file_name: str) -> Path:
            empty_file_path = log_group_directory / file_name
            with empty_file_path.open("w", encoding="utf-8"):
                """We just need to create an empty file to which we will log later"""
            return empty_file_path

        log_group_directory = self.safe_settings_delayed.log_path / group_name
        log_group_directory.mkdir(parents=True, exist_ok=True)

        latest_log_file_name = "latest.log"
        latest_log_path = create_empty_file(latest_log_file_name)

        keep_history = self.safe_settings_delayed.log_keep_history
        if not keep_history:
            return (latest_log_path,)

        dated_log_file_name = f"{LAUNCH_TIME.strftime('%Y-%m-%d_%H-%M-%S')}.log"
        dated_log_path = create_empty_file(dated_log_file_name)

        return dated_log_path, latest_log_path

    def _remove_stream_handlers(self) -> None:
        """Remove all handlers that log to stdout and stderr."""
        core: Core = loguru_logger._core  # type: ignore[attr-defined]
        for handler in core.handlers.values():
            if isinstance(handler._sink, StreamSink):
                loguru_logger.remove(handler._id)

    def _add_file_handlers(self, log_paths: GroupLogFilePaths) -> None:
        for log_level, paths in log_paths.items():
            log_level_3rd_party = self._get_3rd_party_log_level(log_level)

            for path in paths:
                loguru_logger.add(
                    sink=path,
                    format=LOG_FORMAT,
                    filter=self._make_filter(level=log_level, level_3rd_party=log_level_3rd_party),
                )

    def _get_3rd_party_log_level(self, log_level: str) -> str:
        """
        Return the log level for 3rd party modules based on given log_level for clive.

        We want to include everything when clive is in DEBUG mode, but also leave the option to set a different log lvl
        for 3rd party modules when clive is in higher log levels than DEBUG.

        """
        log_level_3rd_party = self.safe_settings_delayed.log_level_3rd_party.upper()
        return "DEBUG" if log_level == "DEBUG" else log_level_3rd_party

    def _make_filter(self, *, level: int | str, level_3rd_party: int | str) -> Callable[..., bool]:
        level_no = getattr(logging, level) if isinstance(level, str) else level
        level_no_3rd_party = getattr(logging, level_3rd_party) if isinstance(level_3rd_party, str) else level_3rd_party

        def _filter(record: dict[str, Any]) -> bool:
            is_3rd_party = ROOT_DIRECTORY not in Path(record["file"].path).parents
            if level_no_3rd_party is not None and is_3rd_party:
                return bool(record["level"].no >= level_no_3rd_party)
            return bool(record["level"].no >= level_no)

        return _filter


logger = Logger()

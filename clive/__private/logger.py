from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from loguru import logger as loguru_logger
from loguru._simple_sinks import StreamSink

from clive.__private.core.constants.env import KNOWN_FIRST_PARTY_PACKAGES, LAUNCH_TIME

if TYPE_CHECKING:
    from collections.abc import Callable

    from loguru._logger import Core

    from clive.__private.settings import SafeSettings

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
        def _hooked(*args: Any, **kwargs: Any) -> None:
            try_one_of = f"Try one of: {self.safe_settings_delayed.AVAILABLE_LOG_LEVELS}"

            if self.__enabled_loguru:
                patched = loguru_logger.opt(depth=1)
                loguru_attr = getattr(patched, item, None)
                assert callable(loguru_attr), f"Loguru {item} is not callable. {try_one_of}"
                loguru_attr(*args, **kwargs)
            if self.__enabled_textual:
                from textual import log as textual_logger  # noqa: PLC0415

                textual_log_attr = getattr(textual_logger, item, None)
                assert callable(textual_log_attr), f"Textual {item} is not callable. {try_one_of}"
                textual_log_attr(*args, **kwargs)

        return _hooked

    @property
    def safe_settings_delayed(self) -> SafeSettings:
        from clive.__private.settings import safe_settings  # noqa: PLC0415

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
        log_levels = self.safe_settings_delayed.log.levels
        for log_level in log_levels:
            available_log_levels = self.safe_settings_delayed.AVAILABLE_LOG_LEVELS
            if log_level not in available_log_levels:
                raise RuntimeError(f"Invalid log level: {log_level}, expected one of {available_log_levels}.")

            log_paths[log_level] = self._create_log_files_per_group(group_name=log_level.lower())
        return log_paths

    def _create_log_files_per_group(self, group_name: str) -> LogFilePaths:
        def create_empty_file(file_name: str) -> Path:
            empty_file_path = log_group_directory / file_name
            with empty_file_path.open("w", encoding="utf-8"):
                """We just need to create an empty file to which we will log later"""
            return empty_file_path

        log_group_directory: Path = self.safe_settings_delayed.log.path / group_name
        log_group_directory.mkdir(parents=True, exist_ok=True)

        latest_log_file_name = "latest.log"
        latest_log_path = create_empty_file(latest_log_file_name)

        should_keep_history = self.safe_settings_delayed.log.should_keep_history
        if not should_keep_history:
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
            for path in paths:
                loguru_logger.add(
                    sink=path,
                    format=LOG_FORMAT,
                    filter=self._make_filter(level=log_level),
                )

    def _get_1st_party_log_level(self) -> str:
        return self.safe_settings_delayed.log.level_1st_party

    def _get_3rd_party_log_level(self) -> str:
        return self.safe_settings_delayed.log.level_3rd_party

    def _make_filter(self, *, level: str) -> Callable[..., bool]:
        level_mapping: dict[str, int] = {
            "clive": getattr(logging, level),
            "1st_party": getattr(logging, self._get_1st_party_log_level()),
            "3rd_party": getattr(logging, self._get_3rd_party_log_level()),
        }

        def _filter(record: dict[str, Any]) -> bool:
            is_clive = "clive" in record["name"]
            is_1st_party = any(pkg in record["name"] for pkg in KNOWN_FIRST_PARTY_PACKAGES)

            category = "clive" if is_clive else "1st_party" if is_1st_party else "3rd_party"
            min_required_level_no = level_mapping[category]
            directory_level_no = level_mapping["clive"]
            record_level_no: int = record["level"].no

            return record_level_no >= directory_level_no and record_level_no >= min_required_level_no

        return _filter


logger = Logger()

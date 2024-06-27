from __future__ import annotations

import shutil
from pathlib import Path

from clive.__private.config import ROOT_DIRECTORY, settings
from clive.__private.logger import logger
from clive.__private.safe_settings import safe_settings
from clive.dev import is_in_dev_mode


def prepare_before_launch(*, enable_textual_logger: bool = True, enable_stream_handlers: bool = False) -> None:
    def _create_clive_data_directory() -> None:
        Path(safe_settings.data_path).mkdir(parents=True, exist_ok=True)

    def _copy_settings() -> None:
        user_settings_path = Path(safe_settings.data_path) / "settings.toml"
        if not user_settings_path.is_file():
            shutil.copy(ROOT_DIRECTORY.parent / "settings.toml", user_settings_path)

    if is_in_dev_mode():
        # logger also refers to settings, so we need to set it before logger setup
        settings.setenv("dev")

    logger.setup(enable_textual=enable_textual_logger, enable_stream_handlers=enable_stream_handlers)

    _create_clive_data_directory()
    _copy_settings()

    if is_in_dev_mode():
        logger.warning("Running in development mode.")
        logger.debug(f"settings:\n{settings.as_dict()}")

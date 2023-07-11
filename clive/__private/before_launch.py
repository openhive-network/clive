from __future__ import annotations

import shutil
from pathlib import Path

from clive.__private.config import ROOT_DIRECTORY, settings
from clive.__private.logger import logger


def prepare_before_launch(*, enable_textual_logger: bool = True) -> None:
    def _create_clive_data_directory() -> None:
        Path(settings.DATA_PATH).mkdir(parents=True, exist_ok=True)

    def _copy_settings() -> None:
        user_settings_path = Path(settings.DATA_PATH) / "settings.toml"
        if not user_settings_path.is_file():
            shutil.copy(ROOT_DIRECTORY.parent / "settings.toml", user_settings_path)

    logger.setup(enable_textual=enable_textual_logger)

    _create_clive_data_directory()
    _copy_settings()

    logger.debug(f"settings:\n{settings.as_dict()}")

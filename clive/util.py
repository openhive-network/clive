from __future__ import annotations

from loguru import logger

from clive.config import settings
from clive.logger import configure_logger


def prepare_before_launch() -> None:
    configure_logger()
    logger.debug(f"settings:\n{settings.as_dict()}")

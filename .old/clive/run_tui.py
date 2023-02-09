from __future__ import annotations

from loguru import logger


def run_tui() -> None:
    from clive.config import settings
    from clive.get_clive import get_clive
    from clive.logger import configure_logger

    configure_logger()
    logger.debug(f"settings:\n{settings.as_dict()}")
    get_clive().run()

from __future__ import annotations

from loguru import logger


def run_cli() -> None:
    from clive.cli import cli
    from clive.config import settings
    from clive.logger import configure_logger

    configure_logger()
    logger.debug(f"settings:\n{settings.as_dict()}")
    cli()

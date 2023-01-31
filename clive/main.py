import sys

from loguru import logger

from clive.cli import cli
from clive.config import settings
from clive.logger import configure_logger
from clive.run_tui import run_tui


def main() -> None:
    configure_logger()
    logger.debug(f"settings:\n{settings.as_dict()}")

    if not sys.argv[1:] and sys.stdin.isatty():
        run_tui()
        return

    cli()


if __name__ == "__main__":
    main()

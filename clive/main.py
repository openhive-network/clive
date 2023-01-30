import sys

from loguru import logger

from clive.cli import cli
from clive.config import settings
from clive.get_clive import get_clive
from clive.logger import configure_logger


def main() -> None:
    configure_logger()
    logger.debug(f"settings:\n{settings.as_dict()}")

    if not sys.argv[1:]:
        get_clive().run()
        return

    cli()


if __name__ == "__main__":
    main()

from loguru import logger

from clive.app import clive
from clive.config import settings
from clive.logger import configure_logger


def main() -> None:
    configure_logger()
    logger.debug(f"settings:\n{settings.as_dict()}")
    logger.info("clive.main.main() works!")
    clive.run()


if __name__ == "__main__":
    main()

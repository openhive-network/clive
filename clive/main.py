from loguru import logger

from clive.config import settings
from clive.logger import configure_logger


def main() -> None:
    configure_logger()
    logger.debug(f"settings:\n{settings.as_dict()}")
    logger.info("clive.main.main() works!")


if __name__ == "__main__":
    main()

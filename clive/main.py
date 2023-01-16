from loguru import logger

from clive.logger import configure_logger


def main() -> None:
    configure_logger()
    logger.info("clive.main.main() works!")


if __name__ == "__main__":
    main()

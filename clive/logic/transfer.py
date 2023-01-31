from loguru import logger


def transfer(from_account: str, to_account: str, amount: float, memo: str) -> None:
    logger.info(f"Transfer {amount} from {from_account} to {to_account} with memo {memo}.")

from __future__ import annotations

from clive.__private.core.commands.command import Command
from clive.__private.logger import logger
from clive.models.transfer_operation import TransferOperation


class Transfer(Command[None]):
    def __init__(self, *, from_: str, to: str, amount: str, asset: str, memo: str | None = None) -> None:
        super().__init__()
        self.__from = from_
        self.__to = to
        self.__amount = amount
        self.__asset = asset
        self.__memo = memo

    def execute(self) -> None:
        operation = TransferOperation(
            from_=self.__from,
            to=self.__to,
            amount=self.__amount,
            asset=self.__asset,
            memo=self.__memo,
        )

        # TODO: Some logic that will send the operation to the blockchain

        logger.info(f"Operation sent: {operation}")

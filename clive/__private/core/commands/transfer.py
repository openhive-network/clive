from __future__ import annotations

from clive.__private.core.commands.command import Command
from clive.__private.logger import logger
from clive.models.transfer_operation import TransferOperation


class Transfer(Command):
    @staticmethod
    def execute(*, from_: str, to: str, amount: str, asset: str, memo: str | None = None) -> None:
        operation = TransferOperation(from_=from_, to=to, amount=amount, asset=asset, memo=memo)

        # TODO: Some logic that will send the operation to the blockchain

        logger.info(f"Operation sent: {operation}")

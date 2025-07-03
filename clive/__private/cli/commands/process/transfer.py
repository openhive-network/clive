from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import TransferOperation

if TYPE_CHECKING:
    from clive.__private.models import Asset


@dataclass(kw_only=True)
class Transfer(OperationCommand):
    """
    Class to transfer assets from one account to another.

    Args:
        from_account: The account to transfer assets from.
        to: The account to transfer assets to.
        amount: The amount of assets to transfer.
        memo: An optional memo for the transfer.
    """

    from_account: str
    to: str
    amount: Asset.LiquidT
    memo: str

    async def _create_operation(self) -> TransferOperation:
        """
        Create an operation instance based on the provided parameters.

        Returns:
            TransferOperation: An instance of TransferOperation with the specified parameters.
        """
        return TransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=self.amount,
            memo=self.memo,
        )

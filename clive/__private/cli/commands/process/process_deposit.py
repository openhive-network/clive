from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import TransferToSavingsOperation

if TYPE_CHECKING:
    from clive.__private.models import Asset


@dataclass(kw_only=True)
class ProcessDeposit(OperationCommand):
    """
    Class to process a deposit operation.

    Args:
        from_account: The account from which the deposit is made.
        to_account: The account to which the deposit is made.
        amount: The amount of the deposit.
        memo: A memo for the deposit operation.
    """

    from_account: str
    to_account: str
    amount: Asset.LiquidT
    memo: str

    async def _create_operation(self) -> TransferToSavingsOperation:
        """
        Create an instance based on the provided parameters.

        Returns:
            TransferToSavingsOperation: An operation instance representing the deposit.
        """
        return TransferToSavingsOperation(
            from_=self.from_account,
            to=self.to_account,
            amount=self.amount,
            memo=self.memo,
        )

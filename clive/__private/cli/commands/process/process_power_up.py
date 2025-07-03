from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import TransferToVestingOperation

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class ProcessPowerUp(OperationCommand):
    """
    Class to handle the power-up operation in the Hive blockchain.

    Args:
        from_account: The account initiating the power-up.
        to_account: The account receiving the power-up.
        amount: The amount of Hive to be powered up.
    """

    from_account: str
    to_account: str
    amount: Asset.Hive

    async def _create_operation(self) -> TransferToVestingOperation:
        """
        Create an operation for the power-up operation.

        Returns:
            TransferToVestingOperation: The operation to be executed.
        """
        return TransferToVestingOperation(
            from_=self.from_account,
            to=self.to_account,
            amount=self.amount,
        )

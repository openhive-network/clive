from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import TransferFromSavingsOperation

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.savings_data import SavingsData
    from clive.__private.models import Asset


@dataclass(kw_only=True)
class ProcessWithdrawal(OperationCommand):
    """
    Class to handle the processing of a withdrawal from savings.

    Args:
        from_account: The account from which the funds are withdrawn.
        request_id: The ID of the withdrawal request, if available.
        to_account: The account to which the funds are transferred.
        amount: The amount of funds to withdraw.
        memo: A memo for the transaction.
    """

    from_account: str
    request_id: int | None
    to_account: str
    amount: Asset.LiquidT
    memo: str

    async def _create_operation(self) -> TransferFromSavingsOperation:
        """
        Create an operation for processing the withdrawal.

        If the request ID is not provided, it retrieves the savings data to create a new request ID.

        Returns:
            TransferFromSavingsOperation: The operation to be executed for the withdrawal.
        """
        if self.request_id is None:
            wrapper = await self.world.commands.retrieve_savings_data(account_name=self.profile.accounts.working.name)
            savings_data: SavingsData = wrapper.result_or_raise
            self.request_id = savings_data.create_request_id()

        return TransferFromSavingsOperation(
            from_=self.from_account,
            request_id=self.request_id,
            to=self.to_account,
            amount=self.amount,
            memo=self.memo,
        )

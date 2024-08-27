from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from schemas.operations import TransferFromSavingsOperation

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.savings_data import SavingsData
    from clive.__private.models import Asset


@dataclass(kw_only=True)
class ProcessWithdrawal(OperationCommand):
    from_account: str
    request_id: int | None
    to_account: str
    amount: Asset.LiquidT
    memo: str

    async def _create_operation(self) -> TransferFromSavingsOperation:
        if self.request_id is None:
            wrapper = await self.world.commands.retrieve_savings_data(
                account_name=self.world.profile.accounts.working.name
            )
            savings_data: SavingsData = wrapper.result_or_raise
            self.request_id = savings_data.create_request_id()

        return TransferFromSavingsOperation(
            from_=self.from_account,
            request_id=self.request_id,
            to=self.to_account,
            amount=self.amount,
            memo=self.memo,
        )

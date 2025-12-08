from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.memo_command import MemoCommand
from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import TransferFromSavingsOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.core.commands.data_retrieval.savings_data import SavingsData
    from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class ProcessWithdrawal(OperationCommand, MemoCommand):
    from_account: str
    request_id: int | None
    to_account: str
    amount: Asset.LiquidT

    @property
    def request_id_ensure(self) -> int:
        assert self.request_id is not None, "request_id should be set at this point"
        return self.request_id

    async def fetch_data(self) -> None:
        await super().fetch_data()
        if self.request_id is None:
            wrapper = await self.world.commands.retrieve_savings_data(account_name=self.profile.accounts.working.name)
            savings_data: SavingsData = wrapper.result_or_raise
            self.request_id = savings_data.create_request_id()

    async def _create_operations(self) -> ComposeTransaction:
        yield TransferFromSavingsOperation(
            from_=self.from_account,
            request_id=self.request_id_ensure,
            to=self.to_account,
            amount=self.amount,
            memo=self.ensure_memo,
        )

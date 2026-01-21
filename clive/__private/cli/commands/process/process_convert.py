from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import CollateralizedConvertOperation, ConvertOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.core.commands.data_retrieval.convert_data import ConvertData
    from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class ProcessConvert(OperationCommand):
    owner: str
    amount: Asset.Hbd
    request_id: int | None = None

    @property
    def request_id_ensure(self) -> int:
        assert self.request_id is not None, "request_id should be set at this point"
        return self.request_id

    async def fetch_data(self) -> None:
        await super().fetch_data()
        if self.request_id is None:
            wrapper = await self.world.commands.retrieve_convert_data(account_name=self.profile.accounts.working.name)
            convert_data: ConvertData = wrapper.result_or_raise
            self.request_id = convert_data.create_request_id()

    async def _create_operations(self) -> ComposeTransaction:
        yield ConvertOperation(
            owner=self.owner,
            requestid=self.request_id_ensure,
            amount=self.amount,
        )


@dataclass(kw_only=True)
class ProcessCollateralizedConvert(OperationCommand):
    owner: str
    amount: Asset.Hive
    request_id: int | None = None

    @property
    def request_id_ensure(self) -> int:
        assert self.request_id is not None, "request_id should be set at this point"
        return self.request_id

    async def fetch_data(self) -> None:
        await super().fetch_data()
        if self.request_id is None:
            wrapper = await self.world.commands.retrieve_convert_data(account_name=self.profile.accounts.working.name)
            convert_data: ConvertData = wrapper.result_or_raise
            self.request_id = convert_data.create_request_id()

    async def _create_operations(self) -> ComposeTransaction:
        yield CollateralizedConvertOperation(
            owner=self.owner,
            requestid=self.request_id_ensure,
            amount=self.amount,
        )

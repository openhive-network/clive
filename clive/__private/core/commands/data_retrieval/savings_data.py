from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_data_retrieval import (
    CommandDataRetrieval,
)

if TYPE_CHECKING:
    from clive.__private.core.node import Node
    from clive.models.aliased import DynamicGlobalProperties, SavingsWithdrawals, SchemasAccount
    from schemas.apis.database_api import FindAccounts, FindSavingsWithdrawals


@dataclass
class HarvestedDataRaw:
    dgpo: DynamicGlobalProperties | None = None
    core_account: FindAccounts | None = None
    savings_withdrawals: FindSavingsWithdrawals | None = None


@dataclass
class SanitizedData:
    dgpo: DynamicGlobalProperties
    core_account: SchemasAccount
    pending_transfers: list[SavingsWithdrawals]


@dataclass
class SavingsData:
    hbd_interest_rate: int = 1000
    pending_transfers: list[SavingsWithdrawals] | None = None
    last_interest_payment: datetime = field(default_factory=lambda: datetime.utcfromtimestamp(0))

    def create_request_id(self) -> int:
        return 0


@dataclass(kw_only=True)
class SavingsDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, SavingsData]):
    node: Node
    account_name: str

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with self.node.batch() as node:
            return HarvestedDataRaw(
                await node.api.database_api.get_dynamic_global_properties(),
                await node.api.database_api.find_accounts(accounts=[self.account_name]),
                await node.api.database_api.find_savings_withdrawals(account=self.account_name),
            )

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        return SanitizedData(
            dgpo=self.__assert_gdpo(data.dgpo),
            core_account=self.__assert_core_account(data.core_account),
            pending_transfers=self.__assert_pending_transfers(data.savings_withdrawals),
        )

    async def _process_data(self, data: SanitizedData) -> SavingsData:
        return SavingsData(
            hbd_interest_rate=data.dgpo.hbd_interest_rate,
            last_interest_payment=data.core_account.savings_hbd_last_interest_payment,
            pending_transfers=data.pending_transfers,
        )

    def __assert_gdpo(self, data: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert data is not None, "DynamicGlobalProperties data is missing"
        return data

    def __assert_core_account(self, data: FindAccounts | None) -> SchemasAccount:
        assert data is not None, "FindAccounts data is missing"
        assert len(data.accounts) == 1, "Invalid amount of accounts"

        account = data.accounts[0]
        assert account.name == self.account_name, "Invalid account name"
        return account

    def __assert_pending_transfers(self, data: FindSavingsWithdrawals | None) -> list[SavingsWithdrawals]:
        assert data is not None, "FindSavingsWithdrawals data is missing"
        return data.withdrawals

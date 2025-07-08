from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from beekeepy.exceptions import UnknownDecisionPathError

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.formatters.humanize import align_to_dot, humanize_asset
from clive.exceptions import RequestIdError

if TYPE_CHECKING:
    from datetime import datetime

    from clive.__private.core.node import Node
    from clive.__private.models import Asset
    from clive.__private.models.schemas import (
        Account,
        DynamicGlobalProperties,
        FindAccounts,
        FindSavingsWithdrawals,
        SavingsWithdrawal,
        TransferFromSavingsOperation,
    )


@dataclass
class HarvestedDataRaw:
    dgpo: DynamicGlobalProperties | None = None
    core_account: FindAccounts | None = None
    savings_withdrawals: FindSavingsWithdrawals | None = None


@dataclass
class SanitizedData:
    dgpo: DynamicGlobalProperties
    core_account: Account
    pending_transfers: list[SavingsWithdrawal]


@dataclass
class SavingsData:
    hbd_interest_rate: int
    pending_transfers: list[SavingsWithdrawal]
    last_interest_payment: datetime
    hive_savings_balance: Asset.Hive
    hbd_savings_balance: Asset.Hbd
    hbd_unclaimed: Asset.Hbd

    def create_request_id(self, *, future_transfers: list[TransferFromSavingsOperation] | None = None) -> int:
        """
        Calculate the next available request id for TransferFromSavingsOperation.

        Args:
            future_transfers: Future transfers to include in calculation. (e.g. already stored in the cart)

        Raises:
            RequestIdError: If the maximum number of request ids is exceeded.

        Returns:
            The next available request id.
        """
        max_number_of_request_ids: Final[int] = 100

        future_transfers = future_transfers or []
        all_transfers = self.pending_transfers + future_transfers
        if not all_transfers:
            return 0

        if len(all_transfers) >= max_number_of_request_ids:
            raise RequestIdError("Maximum quantity of request ids is 100")

        last_occupied_id = max(all_transfers, key=lambda transfer: transfer.request_id).request_id
        return last_occupied_id + 1

    def get_pending_transfers_aligned_amounts(self) -> list[str]:
        """Return dot-aligned amounts of pending transfers."""
        amounts_to_align = [f"{humanize_asset(transfer.amount)}" for transfer in self.pending_transfers]

        return align_to_dot(*amounts_to_align)


@dataclass(kw_only=True)
class SavingsDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, SavingsData]):
    node: Node
    account_name: str

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with await self.node.batch() as node:
            return HarvestedDataRaw(
                await node.api.database_api.get_dynamic_global_properties(),
                await node.api.database_api.find_accounts(accounts=[self.account_name]),
                await node.api.database_api.find_savings_withdrawals(account=self.account_name),
            )
        raise UnknownDecisionPathError(f"{self.__class__.__name__}:_harvest_data_from_api")

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
            hbd_savings_balance=data.core_account.savings_hbd_balance,
            hive_savings_balance=data.core_account.savings_balance,
            hbd_unclaimed=data.core_account.reward_hbd_balance,
        )

    def __assert_gdpo(self, data: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert data is not None, "DynamicGlobalProperties data is missing"
        return data

    def __assert_core_account(self, data: FindAccounts | None) -> Account:
        assert data is not None, "FindAccounts data is missing"
        assert len(data.accounts) == 1, "Invalid amount of accounts"

        account = data.accounts[0]
        assert account.name == self.account_name, "Invalid account name"
        return account

    def __assert_pending_transfers(self, data: FindSavingsWithdrawals | None) -> list[SavingsWithdrawal]:
        assert data is not None, "FindSavingsWithdrawals data is missing"
        return data.withdrawals

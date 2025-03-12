from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from beekeepy.exceptions import UnknownDecisionPathError

from clive.__private.core import iwax
from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.formatters.humanize import align_to_dot
from clive.__private.models import Asset, HpVestsBalance

if TYPE_CHECKING:
    from datetime import datetime
    from decimal import Decimal

    from clive.__private.core.node import Node
    from clive.__private.models.schemas import (
        Account,
        DynamicGlobalProperties,
        FindAccounts,
        FindVestingDelegations,
        ListWithdrawVestingRoutes,
        VestingDelegation,
        WithdrawRoute,
    )

_MAX_WITHDRAW_VESTING_ROUTES_LIMIT: Final[int] = 10


@dataclass
class HarvestedDataRaw:
    gdpo: DynamicGlobalProperties | None = None
    core_account: FindAccounts | None = None
    withdraw_routes: ListWithdrawVestingRoutes | None = None
    delegations: FindVestingDelegations | None = None


@dataclass
class SanitizedData:
    gdpo: DynamicGlobalProperties
    core_account: Account
    withdraw_routes: list[WithdrawRoute]
    delegations: list[VestingDelegation]


@dataclass
class HivePowerData:
    owned_balance: HpVestsBalance
    total_balance: HpVestsBalance
    received_balance: HpVestsBalance
    delegated_balance: HpVestsBalance
    next_vesting_withdrawal: datetime
    withdraw_routes: list[WithdrawRoute]
    delegations: list[VestingDelegation]
    to_withdraw: HpVestsBalance
    withdrawn: HpVestsBalance
    remaining: HpVestsBalance
    next_power_down: HpVestsBalance
    current_hp_apr: Decimal
    gdpo: DynamicGlobalProperties

    def get_delegations_aligned_amounts(self) -> tuple[list[str], list[str]]:
        """Return aligned amounts of delegations in HP and VESTS."""
        hp_amounts_to_align, vests_amounts_to_align = [], []
        for delegation in self.delegations:
            hp_vests_amount = HpVestsBalance.create(delegation.vesting_shares, self.gdpo)

            hp_amounts_to_align.append(Asset.pretty_amount(hp_vests_amount.hp_balance))
            vests_amounts_to_align.append(Asset.pretty_amount(hp_vests_amount.vests_balance))

        return align_to_dot(*hp_amounts_to_align), align_to_dot(*vests_amounts_to_align)


@dataclass(kw_only=True)
class HivePowerDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, HivePowerData]):
    node: Node
    account_name: str

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with await self.node.batch() as node:
            return HarvestedDataRaw(
                await node.api.database_api.get_dynamic_global_properties(),
                await node.api.database_api.find_accounts(accounts=[self.account_name]),
                await node.api.database_api.list_withdraw_vesting_routes(
                    start=(self.account_name, ""), limit=_MAX_WITHDRAW_VESTING_ROUTES_LIMIT, order="by_withdraw_route"
                ),
                await node.api.database_api.find_vesting_delegations(account=self.account_name),
            )
        raise UnknownDecisionPathError(f"{self.__class__.__name__}:_harvest_data_from_api")

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        return SanitizedData(
            gdpo=self._assert_gdpo(data.gdpo),
            core_account=self._assert_core_account(data.core_account),
            withdraw_routes=self._assert_withdraw_routes(data.withdraw_routes),
            delegations=self._assert_delegations(data.delegations),
        )

    async def _process_data(self, data: SanitizedData) -> HivePowerData:
        owned_shares = data.core_account.vesting_shares
        received_shares = data.core_account.received_vesting_shares
        delegated_shares = data.core_account.delegated_vesting_shares
        total_shares = owned_shares + received_shares - delegated_shares - data.core_account.vesting_withdraw_rate
        to_withdraw_vests = iwax.vests(data.core_account.to_withdraw.value)
        withdrawn_vests = iwax.vests(data.core_account.withdrawn.value)
        remaining_vests = to_withdraw_vests - withdrawn_vests

        return HivePowerData(
            owned_balance=HpVestsBalance.create(owned_shares, data.gdpo),
            total_balance=HpVestsBalance.create(total_shares, data.gdpo),
            received_balance=HpVestsBalance.create(received_shares, data.gdpo),
            delegated_balance=HpVestsBalance.create(delegated_shares, data.gdpo),
            next_vesting_withdrawal=data.core_account.next_vesting_withdrawal.value,
            withdraw_routes=[route for route in data.withdraw_routes if route.from_account == self.account_name],
            delegations=data.delegations,
            to_withdraw=HpVestsBalance.create(to_withdraw_vests, data.gdpo),
            withdrawn=HpVestsBalance.create(withdrawn_vests, data.gdpo),
            remaining=HpVestsBalance.create(remaining_vests, data.gdpo),
            next_power_down=HpVestsBalance.create(data.core_account.vesting_withdraw_rate, data.gdpo),
            current_hp_apr=iwax.calculate_hp_apr(data.gdpo),
            gdpo=data.gdpo,
        )

    def _assert_gdpo(self, data: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert data is not None, "DynamicGlobalProperties data is missing"
        return data

    def _assert_core_account(self, data: FindAccounts | None) -> Account:
        assert data is not None, "FindAccounts data is missing"
        assert len(data.accounts) == 1, "Invalid amount of accounts"

        account = data.accounts[0]
        assert account.name == self.account_name, "Invalid account name"
        return account

    def _assert_withdraw_routes(self, data: ListWithdrawVestingRoutes | None) -> list[WithdrawRoute]:
        assert data is not None, "ListWithdrawVestingRoutes data is missing"
        return data.routes

    def _assert_delegations(self, data: FindVestingDelegations | None) -> list[VestingDelegation]:
        assert data is not None, "FindVestingDelegations data is missing"
        return data.delegations

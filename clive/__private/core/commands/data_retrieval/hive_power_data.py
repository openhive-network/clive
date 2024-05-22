from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from clive.__private.core import iwax
from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.hive_vests_conversions import vests_to_hive

if TYPE_CHECKING:
    from datetime import datetime
    from decimal import Decimal

    from clive.__private.core.node import Node
    from clive.models import Asset
    from clive.models.aliased import DynamicGlobalProperties, SchemasAccount
    from schemas.apis.database_api import FindAccounts, FindVestingDelegations, ListWithdrawVestingRoutes
    from schemas.apis.database_api.fundaments_of_reponses import VestingDelegationsFundament as VestingDelegation
    from schemas.apis.database_api.fundaments_of_reponses import WithdrawVestingRoutesFundament as WithdrawRoute

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
    core_account: SchemasAccount
    withdraw_routes: list[WithdrawRoute]
    delegations: list[VestingDelegation[Asset.Vests]]


@dataclass
class SharesBalance:
    """Class to store the balance of shares in HP and VESTS."""

    hp_balance: Asset.Hive
    vests_balance: Asset.Vests


@dataclass
class HivePowerData:
    owned_balance: SharesBalance
    total_balance: SharesBalance
    received_balance: SharesBalance
    delegated_balance: SharesBalance
    next_vesting_withdrawal: datetime
    withdraw_routes: list[WithdrawRoute]
    delegations: list[VestingDelegation[Asset.Vests]]
    to_withdraw: SharesBalance
    withdrawn: SharesBalance
    remaining: SharesBalance
    next_power_down: SharesBalance
    current_hp_apr: Decimal
    gdpo: DynamicGlobalProperties


@dataclass(kw_only=True)
class HivePowerDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, HivePowerData]):
    node: Node
    account_name: str

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with self.node.batch() as node:
            return HarvestedDataRaw(
                await node.api.database_api.get_dynamic_global_properties(),
                await node.api.database_api.find_accounts(accounts=[self.account_name]),
                await node.api.database_api.list_withdraw_vesting_routes(
                    start=(self.account_name, ""), limit=_MAX_WITHDRAW_VESTING_ROUTES_LIMIT, order="by_withdraw_route"
                ),
                await node.api.database_api.find_vesting_delegations(account=self.account_name),
            )

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
        to_withdraw_vests = iwax.vests(data.core_account.to_withdraw)
        withdrawn_vests = iwax.vests(data.core_account.withdrawn)
        remaining_vests = to_withdraw_vests - withdrawn_vests

        return HivePowerData(
            owned_balance=self._create_balance_representation(data.gdpo, owned_shares),
            total_balance=self._create_balance_representation(data.gdpo, total_shares),
            received_balance=self._create_balance_representation(data.gdpo, received_shares),
            delegated_balance=self._create_balance_representation(data.gdpo, delegated_shares),
            next_vesting_withdrawal=data.core_account.next_vesting_withdrawal,
            withdraw_routes=[route for route in data.withdraw_routes if route.from_account == self.account_name],
            delegations=data.delegations,
            to_withdraw=self._create_balance_representation(data.gdpo, to_withdraw_vests),
            withdrawn=self._create_balance_representation(data.gdpo, withdrawn_vests),
            remaining=self._create_balance_representation(data.gdpo, remaining_vests),
            next_power_down=self._create_balance_representation(data.gdpo, data.core_account.vesting_withdraw_rate),
            current_hp_apr=iwax.calculate_hp_apr(data.gdpo),
            gdpo=data.gdpo,
        )

    def _assert_gdpo(self, data: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert data is not None, "DynamicGlobalProperties data is missing"
        return data

    def _assert_core_account(self, data: FindAccounts | None) -> SchemasAccount:
        assert data is not None, "FindAccounts data is missing"
        assert len(data.accounts) == 1, "Invalid amount of accounts"

        account = data.accounts[0]
        assert account.name == self.account_name, "Invalid account name"
        return account

    def _assert_withdraw_routes(self, data: ListWithdrawVestingRoutes | None) -> list[WithdrawRoute]:
        assert data is not None, "ListWithdrawVestingRoutes data is missing"
        return data.routes

    def _assert_delegations(self, data: FindVestingDelegations | None) -> list[VestingDelegation[Asset.Vests]]:
        assert data is not None, "FindVestingDelegations data is missing"
        return data.delegations

    def _create_balance_representation(self, gdpo: DynamicGlobalProperties, vests_value: Asset.Vests) -> SharesBalance:
        return SharesBalance(hp_balance=vests_to_hive(vests_value, gdpo), vests_balance=vests_value)

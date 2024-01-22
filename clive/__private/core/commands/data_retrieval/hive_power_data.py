from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.vests_to_hive import vests_to_hive
from clive.models import Asset

if TYPE_CHECKING:
    from datetime import datetime

    from clive.__private.core.node import Node
    from clive.models.aliased import DynamicGlobalProperties, SchemasAccount
    from schemas.apis.database_api import FindAccounts, FindVestingDelegations, ListWithdrawVestingRoutes
    from schemas.apis.database_api.fundaments_of_reponses import VestingDelegationsFundament as VestingDelegation
    from schemas.apis.database_api.fundaments_of_reponses import WithdrawVestingRoutesFundament as WithdrawRoute


@dataclass
class HarvestedDataRaw:
    dgpo: DynamicGlobalProperties | None = None
    core_account: FindAccounts | None = None
    withdraw_routes: ListWithdrawVestingRoutes | None = None
    delegations: FindVestingDelegations | None = None


@dataclass
class SanitizedData:
    dgpo: DynamicGlobalProperties
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
    next_power_down: SharesBalance
    current_hp_apr: str
    dgpo: DynamicGlobalProperties


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
                    start=(self.account_name, ""), limit=10, order="by_withdraw_route"
                ),
                await node.api.database_api.find_vesting_delegations(account=self.account_name),
            )

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        return SanitizedData(
            dgpo=self._assert_gdpo(data.dgpo),
            core_account=self._assert_core_account(data.core_account),
            withdraw_routes=self._assert_withdraw_routes(data.withdraw_routes),
            delegations=self._assert_delegations(data.delegations),
        )

    async def _process_data(self, data: SanitizedData) -> HivePowerData:
        owned_shares = data.core_account.vesting_shares
        received_shares = data.core_account.received_vesting_shares
        delegated_shares = data.core_account.delegated_vesting_shares
        total_shares = owned_shares + received_shares - delegated_shares - data.core_account.vesting_withdraw_rate

        return HivePowerData(
            owned_balance=self._create_balance_representation(data.dgpo, owned_shares),
            total_balance=self._create_balance_representation(data.dgpo, total_shares),
            received_balance=self._create_balance_representation(data.dgpo, received_shares),
            delegated_balance=self._create_balance_representation(data.dgpo, delegated_shares),
            next_vesting_withdrawal=data.core_account.next_vesting_withdrawal,
            withdraw_routes=[route for route in data.withdraw_routes if route.from_account == self.account_name],
            delegations=data.delegations,
            to_withdraw=self._create_balance_representation(
                data.dgpo, Asset.vests(data.core_account.to_withdraw / 10**data.dgpo.total_vesting_shares.precision)
            ),
            next_power_down=self._create_balance_representation(data.dgpo, data.core_account.vesting_withdraw_rate),
            current_hp_apr=self._calculate_current_hp_apr(data.dgpo),
            dgpo=data.dgpo,
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

    def _create_balance_representation(self, dgdpo: DynamicGlobalProperties, vests_value: Asset.Vests) -> SharesBalance:
        return SharesBalance(hp_balance=vests_to_hive(vests_value, dgdpo), vests_balance=vests_value)

    def _calculate_current_hp_apr(self, gdpo: DynamicGlobalProperties) -> str:
        # The inflation was set to 9.5% at block 7m
        initial_inflation_rate: Final[float] = 9.5
        initial_block: Final[int] = 7000000

        # It decreases by 0.01% every 250k blocks
        decrease_rate: Final[int] = 250000
        decrease_percent_per_increment: Final[float] = 0.01

        # How many increments have happened since block 7m?
        head_block = gdpo.head_block_number
        delta_blocks = head_block - initial_block
        decrease_increments = delta_blocks / decrease_rate

        current_inflation_rate = initial_inflation_rate - decrease_increments * decrease_percent_per_increment

        # Cannot go lower than 0.95 %
        minimum_inflation_rate: Final[float] = 0.95

        if current_inflation_rate < minimum_inflation_rate:
            current_inflation_rate = 0.95

        # Calculate the APR
        vesting_reward_percent = gdpo.vesting_reward_percent / 10000
        virtual_supply = int(gdpo.virtual_supply.amount) / 10**gdpo.virtual_supply.precision
        total_vesting_funds = int(gdpo.total_vesting_fund_hive.amount) / 10**gdpo.total_vesting_fund_hive.precision

        return f"{virtual_supply * current_inflation_rate * vesting_reward_percent / total_vesting_funds :.2f}"

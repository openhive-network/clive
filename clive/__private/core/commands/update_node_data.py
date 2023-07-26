from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from math import ceil
from typing import TYPE_CHECKING, Final, cast

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.iwax import calculate_current_manabar_value, calculate_manabar_full_regeneration_time
from clive.exceptions import CommunicationError
from clive.models import Asset
from schemas.database_api.response_schemas import GetDynamicGlobalProperties

if TYPE_CHECKING:
    from collections.abc import Awaitable, Coroutine
    from types import TracebackType

    from clive.__private.core.node.node import Node
    from clive.__private.storage import mock_database
    from clive.__private.storage.mock_database import Account
    from schemas.__private.hive_fields_custom_schemas import Manabar
    from schemas.database_api.fundaments_of_reponses import AccountItemFundament
    from schemas.rc_api.fundaments_of_responses import RcAccount

    AccountFundamentT = AccountItemFundament[Asset.Hive, Asset.Hbd, Asset.Vests]
    CoreAccountsInfoT = dict[str, AccountFundamentT]
    RcAccountsInfoT = dict[str, RcAccount[Asset.Vests]]


DynamicGlobalPropertiesT = GetDynamicGlobalProperties[Asset.Hive, Asset.Hbd, Asset.Vests]


class SuppressNotExistingApi:
    def __init__(self, api: str) -> None:
        self.__api_name = api

    def __enter__(self) -> None:
        return None

    def __exit__(self, _: type[Exception] | None, ex: Exception | None, __: TracebackType | None) -> bool:
        return ex is None or (isinstance(ex, CommunicationError) and self.__get_formatted_error_message() in str(ex))

    def __get_formatted_error_message(self) -> str:
        return f"Assert Exception:api_itr != data._registered_apis.end(): Could not find API {self.__api_name}"


@dataclass
class UpdateNodeData(CommandWithResult[DynamicGlobalPropertiesT]):
    node: Node
    accounts: list[Account] = field(default_factory=list)

    @dataclass
    class AccountApiInfo:
        core: AccountFundamentT
        latest_interaction: datetime = field(default_factory=lambda: datetime.fromtimestamp(0))
        rc: RcAccount[Asset.Vests] | None = None
        warnings: int = 0
        reputation: int = 0

    async def _async_execute(self) -> None:
        downvote_vote_ratio: Final[int] = 4

        gdpo_future = self.node.api.database_api.get_dynamic_global_properties()
        api_accounts = await self.__harvest_data_from_api()
        gdpo = await gdpo_future
        self._result = gdpo

        for account, info in api_accounts.items():
            account.data.reputation = info.reputation
            account.data.last_transaction = info.latest_interaction
            account.data.warnings = info.warnings

            account.data.hive_balance = info.core.balance
            account.data.hive_dollars = info.core.hbd_balance
            account.data.hive_savings = info.core.savings_balance
            account.data.hbd_savings = info.core.savings_hbd_balance
            account.data.hive_unclaimed = info.core.reward_hive_balance
            account.data.hbd_unclaimed = info.core.reward_hbd_balance
            account.data.hp_unclaimed = info.core.reward_vesting_balance
            account.data.recovery_account = info.core.recovery_account

            account.data.hive_power_balance = self.__calculate_hive_power(gdpo, info.core)

            self.__update_manabar(
                gdpo, int(info.core.post_voting_power.amount), info.core.voting_manabar, account.data.vote_manabar
            )

            self.__update_manabar(
                gdpo,
                int(info.core.post_voting_power.amount) // downvote_vote_ratio,
                info.core.downvote_manabar,
                account.data.downvote_manabar,
            )

            if info.rc is not None:
                self.__update_manabar(gdpo, int(info.rc.max_rc), info.rc.rc_manabar, account.data.rc_manabar)

            account.data.last_refresh = self.__normalize_datetime(datetime.utcnow())

    async def __harvest_data_from_api(self) -> dict[Account, AccountApiInfo]:
        account_names = [acc.name for acc in self.accounts if acc.name]
        if not account_names:
            return {}

        self.__core_accounts_info: CoreAccountsInfoT | None = None

        core_accounts_info_future = self.__submit_gathering_base_information(account_names)
        rc_accounts_info_future = self.__submit_gathering_rc_information(account_names)

        harvested_data: dict[str, tuple[Awaitable[int], Awaitable[int], Awaitable[datetime]]] = {}
        for account in self.accounts:
            harvested_data[account.name] = (
                self.__submit_gathering_account_warnings(account, core_accounts_info_future),
                self.__get_account_reputation(account.name),
                self.__get_newest_account_interactions(account.name),
            )

        await self.__try_await_core_accounts(core_accounts_info_future)
        rc_accounts_info = await rc_accounts_info_future

        assert self.__core_accounts_info is not None
        assert len(self.__core_accounts_info) == len(self.accounts), "invalid amount of accounts after rc api call"
        assert rc_accounts_info == {} or len(rc_accounts_info) == len(
            self.accounts
        ), "invalid amount of accounts after database api call"

        result: dict[Account, UpdateNodeData.AccountApiInfo] = {}
        for account in self.accounts:
            warnings, reputation, last_interaction = harvested_data[account.name]
            result[account] = self.AccountApiInfo(
                core=self.__core_accounts_info[account.name],
                rc=rc_accounts_info.get(account.name),
                latest_interaction=await last_interaction,
                warnings=await warnings,
                reputation=await reputation,
            )
        return result

    async def __submit_gathering_base_information(self, accounts: list[str]) -> CoreAccountsInfoT:
        return {
            str(acc.name): acc for acc in (await self.node.api.database_api.find_accounts(accounts=accounts)).accounts
        }

    async def __submit_gathering_rc_information(self, accounts: list[str]) -> RcAccountsInfoT:
        with SuppressNotExistingApi("rc_api"):
            return {
                acc.account: acc for acc in (await self.node.api.rc_api.find_rc_accounts(accounts=accounts)).rc_accounts
            }
        return {}

    async def __submit_gathering_account_warnings(
        self, account: Account, core_future: Coroutine[None, None, CoreAccountsInfoT]
    ) -> int:
        async def __wait_for_core_info_and_evaluate_warnings() -> int:
            await self.__try_await_core_accounts(core_future)
            assert self.__core_accounts_info is not None
            return sum(
                [
                    await self.__check_for_recurrent_transfers(self.__core_accounts_info[account.name]),
                    await self.__check_is_governance_is_expiring(self.__core_accounts_info[account.name]),
                ]
            )

        part_1_of_sum = __wait_for_core_info_and_evaluate_warnings()
        part_2_of_sum = sum(
            [
                await foo
                for foo in [
                    self.__check_is_recovery_account_not_warning_listed(account),
                    self.__check_is_declining_voting_rights_in_progress(account),
                    self.__check_is_changing_recovery_account_is_in_progress(account),
                    self.__check_is_owner_key_change_is_in_progress(account),
                ]
            ]
        )
        return (await part_1_of_sum) + part_2_of_sum

    async def __try_await_core_accounts(self, awaitable: Awaitable[CoreAccountsInfoT]) -> None:
        if self.__core_accounts_info is None:
            with contextlib.suppress(RuntimeError):  # already awaited
                self.__core_accounts_info = await awaitable

    async def __check_is_recovery_account_not_warning_listed(self, account: Account) -> int:
        warning_recovery_accounts: Final[set[str]] = {"steem"}
        return int(account.data.recovery_account in warning_recovery_accounts)

    async def __check_is_declining_voting_rights_in_progress(self, account: Account) -> int:
        requests = (
            await self.node.api.database_api.list_decline_voting_rights_requests(
                start=account.name, limit=1, order="by_account"
            )
        ).requests
        return int(bool(requests) and requests[0].account == account.name)

    async def __check_is_changing_recovery_account_is_in_progress(self, account: Account) -> int:
        requests = (
            await self.node.api.database_api.list_change_recovery_account_requests(
                start=account.name, limit=1, order="by_account"
            )
        ).requests
        return int(bool(requests) and requests[0].account_to_recover == account.name)

    async def __check_is_owner_key_change_is_in_progress(self, account: Account) -> int:
        owner_auths = (
            await self.node.api.database_api.list_owner_histories(
                start=(account.name, datetime.fromtimestamp(0)), limit=1
            )
        ).owner_auths
        return int(bool(owner_auths) and owner_auths[0].account == account.name)

    async def __check_for_recurrent_transfers(self, account_info: AccountFundamentT) -> int:
        assert account_info is not None, "account_info.core cannot be None"
        return int(account_info.open_recurrent_transfers > 0)

    async def __check_is_governance_is_expiring(self, account_info: AccountFundamentT) -> int:
        assert account_info is not None, "account_info.core cannot be None"
        warning_period_in_days: Final[int] = 31
        return int(
            account_info.governance_vote_expiration_ts - timedelta(days=warning_period_in_days)
            > self.__normalize_datetime(datetime.utcnow())
        )

    async def __get_newest_account_interactions(self, account_name: str) -> datetime:
        non_virtual_operations_filter: Final[int] = 0x3FFFFFFFFFFFF
        return self.__normalize_datetime(
            (
                await self.node.api.account_history_api.get_account_history(
                    account=account_name,
                    limit=1,
                    operation_filter_low=non_virtual_operations_filter,
                    include_reversible=True,
                )
            )
            .history[0][1]
            .timestamp
        )

    async def __get_account_reputation(self, account_name: str) -> int:
        with SuppressNotExistingApi("reputation_api"):
            reputation = (
                await self.node.api.reputation_api.get_account_reputations(account_lower_bound=account_name, limit=1)
            ).reputations
            assert len(reputation) == 1
            assert reputation[0].account == account_name, "reputation data malformed"
            return int(reputation[0].reputation)
        return 0

    def __calculate_hive_power(
        self,
        gdpo: DynamicGlobalPropertiesT,
        account: AccountItemFundament[Asset.Hive, Asset.Hbd, Asset.Vests],
    ) -> int:
        account_vesting_shares = (
            int(account.vesting_shares.amount)
            - int(account.delegated_vesting_shares.amount)
            + int(account.received_vesting_shares.amount)
        )
        return cast(
            int,
            ceil(
                int(self.__vests_to_hive(account_vesting_shares, gdpo).amount)
                / (10 ** gdpo.total_reward_fund_hive.get_asset_information().precision)
            ),
        )

    def __update_manabar(
        self, gdpo: DynamicGlobalPropertiesT, max_mana: int, manabar: Manabar, dest: mock_database.Manabar
    ) -> None:
        power_from_api = int(manabar.current_mana)
        last_update = int(manabar.last_update_time)
        dest.max_value = int(self.__vests_to_hive(max_mana, gdpo).amount)
        dest.value = int(
            self.__vests_to_hive(
                calculate_current_manabar_value(
                    now=int(gdpo.time.timestamp()),
                    max_mana=max_mana,
                    current_mana=power_from_api,
                    last_update_time=last_update,
                ),
                gdpo,
            ).amount
        )

        dest.full_regeneration = (
            calculate_manabar_full_regeneration_time(
                now=int(gdpo.time.timestamp()),
                max_mana=max_mana,
                current_mana=power_from_api,
                last_update_time=last_update,
            )
            - gdpo.time
        )

    def __vests_to_hive(self, amount: int | Asset.Vests, gdpo: DynamicGlobalPropertiesT) -> Asset.Hive:
        if isinstance(amount, Asset.Vests):
            amount = int(amount.amount)
        return Asset.Hive(
            amount=int(amount * int(gdpo.total_vesting_fund_hive.amount) / int(gdpo.total_vesting_shares.amount))
        )

    def __normalize_datetime(self, date: datetime) -> datetime:
        return date.replace(microsecond=0, tzinfo=timezone.utc)

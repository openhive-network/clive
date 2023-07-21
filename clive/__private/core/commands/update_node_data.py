from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from math import ceil
from typing import TYPE_CHECKING, Final, cast

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.iwax import (
    calculate_current_manabar_value,
    calculate_manabar_full_regeneration_time,
)
from clive.__private.stopwatch import Stopwatch
from clive.exceptions import CommunicationError
from clive.models import Asset
from schemas.database_api.response_schemas import (
    FindAccounts,
    GetDynamicGlobalProperties,
    ListChangeRecoveryAccountRequests,
    ListDeclineVotingRightsRequests,
    ListOwnerHistories,
)

if TYPE_CHECKING:
    from types import TracebackType

    from clive.__private.core.node.node import Node
    from clive.__private.storage import mock_database
    from clive.__private.storage.accounts import Account
    from schemas.__private.hive_fields_custom_schemas import Manabar
    from schemas.account_history_api.response_schemas import GetAccountHistory
    from schemas.database_api.fundaments_of_reponses import AccountItemFundament
    from schemas.rc_api.fundaments_of_responses import RcAccount
    from schemas.rc_api.response_schemas import FindRcAccounts
    from schemas.reputation_api.response_schemas import GetAccountReputations

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
    class _AccountApiInfo:
        core: AccountFundamentT
        last_history_entry: datetime = field(default_factory=lambda: datetime.fromtimestamp(0))
        rc: RcAccount[Asset.Vests] | None = None
        warnings: int = 0
        reputation: int = 0

    @dataclass
    class _HarvestedData:
        core_raw: AccountFundamentT | None = None
        rc_raw: RcAccount[Asset.Vests] | None = None
        reputation_raw: GetAccountReputations | None = None
        last_interaction_info_raw: GetAccountHistory | None = None
        decline_voting_rights_raw: ListDeclineVotingRightsRequests | None = None
        recovery_account_in_progress: ListChangeRecoveryAccountRequests | None = None
        owner_key_change_in_progress: ListOwnerHistories | None = None

    async def _execute(self) -> None:
        self._result = await self.node.api.database_api.get_dynamic_global_properties()
        if not self.accounts:
            return

        with Stopwatch("harvesting"):
            api_accounts = await self.__harvest_data_from_api()

        with Stopwatch("processing"):
            self.__process_data(api_accounts)

    def __process_data(self, api_accounts: dict[Account, _AccountApiInfo]) -> None:
        downvote_vote_ratio: Final[int] = 4

        gdpo = self._result
        assert gdpo is not None  # mypy check

        for account, info in api_accounts.items():
            account.data.reputation = info.reputation
            account.data.last_history_entry = info.last_history_entry
            account.data.last_account_update = info.core.last_account_update
            account.data.warnings = info.warnings

            account.data.hive_balance = info.core.balance
            account.data.hbd_balance = info.core.hbd_balance
            account.data.hive_savings = info.core.savings_balance
            account.data.hbd_savings = info.core.savings_hbd_balance
            account.data.hbd_reward_balance = info.core.reward_hbd_balance
            account.data.hive_unclaimed = info.core.reward_hive_balance
            account.data.hbd_unclaimed = info.core.reward_hbd_balance
            account.data.hp_unclaimed = info.core.reward_vesting_balance
            account.data.recovery_account = info.core.recovery_account
            account.data.savings_hbd_last_interest_payment = info.core.savings_hbd_last_interest_payment

            account.data.hp_balance = self.__calculate_hive_power(gdpo, info.core)

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

    async def __harvest_data_from_api(self) -> dict[Account, _AccountApiInfo]:
        non_virtual_operations_filter: Final[int] = 0x3FFFFFFFFFFFF

        account_names = [acc.name for acc in self.accounts if acc.name]
        if not account_names:
            return {}

        core_accounts_raw: FindAccounts | None = None
        rc_accounts_raw: FindRcAccounts[Asset.Vests] | None = None
        harvested_data: defaultdict[str, UpdateNodeData._HarvestedData] = defaultdict(
            lambda: UpdateNodeData._HarvestedData()
        )

        async with self.node.batch() as node:
            core_accounts_raw = await node.api.database_api.find_accounts(accounts=account_names)
            rc_accounts_raw = await node.api.rc_api.find_rc_accounts(accounts=account_names)

            for account in self.accounts:
                harvested_data[account.name].reputation_raw = await node.api.reputation_api.get_account_reputations(
                    account_lower_bound=account.name, limit=1
                )

                harvested_data[account.name].last_interaction_info_raw = (
                    await node.api.account_history_api.get_account_history(
                        account=account.name,
                        limit=1,
                        operation_filter_low=non_virtual_operations_filter,
                        include_reversible=True,
                    )
                )

                harvested_data[account.name].decline_voting_rights_raw = (
                    await node.api.database_api.list_decline_voting_rights_requests(
                        start=account.name, limit=1, order="by_account"
                    )
                )
                harvested_data[account.name].recovery_account_in_progress = (
                    await node.api.database_api.list_change_recovery_account_requests(
                        start=account.name, limit=1, order="by_account"
                    )
                )
                harvested_data[account.name].owner_key_change_in_progress = (
                    await node.api.database_api.list_owner_histories(
                        start=(account.name, datetime.fromtimestamp(0)), limit=1
                    )
                )

        assert core_accounts_raw is not None, "core accounts cannot be not"
        assert len(core_accounts_raw.accounts) == len(
            self.accounts
        ), "invalid amount of accounts after database api call"
        assert len(harvested_data) == len(self.accounts), "not all accounts has been processed"

        with SuppressNotExistingApi("rc_api"):
            assert len(rc_accounts_raw.rc_accounts) == len(
                self.accounts
            ), "invalid amount of accounts after rc api call"
            for rc_account in rc_accounts_raw.rc_accounts:
                harvested_data[rc_account.account].rc_raw = rc_account

        for core_account in core_accounts_raw.accounts:
            harvested_data[core_account.name].core_raw = core_account

        result: dict[Account, UpdateNodeData._AccountApiInfo] = {}
        for account in self.accounts:
            account_data_raw = harvested_data[account.name]
            assert account_data_raw.core_raw is not None  # mypy check
            result[account] = self._AccountApiInfo(
                core=account_data_raw.core_raw,
                rc=account_data_raw.rc_raw,
                last_history_entry=self.__get_account_last_history_entry(account_data_raw),
                warnings=self.__calculate_warnings(account_data_raw),
                reputation=self.__get_account_reputation(account_data_raw),
            )
        return result

    def __get_account_last_history_entry(self, raw: UpdateNodeData._HarvestedData) -> datetime:
        with SuppressNotExistingApi("account_history_api"):
            assert raw.last_interaction_info_raw is not None
            return self.__normalize_datetime(raw.last_interaction_info_raw.history[0][1].timestamp)
        return datetime.fromtimestamp(0, timezone.utc)

    def __calculate_warnings(self, raw: UpdateNodeData._HarvestedData) -> int:
        return sum(
            [
                check(raw)
                for check in [
                    self.__check_for_recurrent_transfers,
                    self.__check_is_governance_is_expiring,
                    self.__check_is_recovery_account_not_warning_listed,
                    self.__check_is_declining_voting_rights_in_progress,
                    self.__check_is_changing_recovery_account_is_in_progress,
                    self.__check_is_owner_key_change_is_in_progress,
                ]
            ]
        )

    def __check_is_recovery_account_not_warning_listed(self, raw: UpdateNodeData._HarvestedData) -> int:
        warning_recovery_accounts: Final[set[str]] = {"steem"}

        assert raw.core_raw is not None  # mypy check

        return int(raw.core_raw.recovery_account in warning_recovery_accounts)

    def __check_is_declining_voting_rights_in_progress(self, raw: UpdateNodeData._HarvestedData) -> int:
        assert raw.decline_voting_rights_raw is not None  # mypy check
        assert raw.core_raw is not None  # mypy check

        requests = raw.decline_voting_rights_raw.requests
        return int(bool(requests) and requests[0].account == raw.core_raw.name)

    def __check_is_changing_recovery_account_is_in_progress(self, raw: UpdateNodeData._HarvestedData) -> int:
        assert raw.recovery_account_in_progress is not None  # mypy check
        assert raw.core_raw is not None  # mypy check

        requests = raw.recovery_account_in_progress.requests
        return int(bool(requests) and requests[0].account_to_recover == raw.core_raw.name)

    def __check_is_owner_key_change_is_in_progress(self, raw: UpdateNodeData._HarvestedData) -> int:
        assert raw.owner_key_change_in_progress is not None  # mypy check
        assert raw.core_raw is not None  # mypy check

        owner_auths = raw.owner_key_change_in_progress.owner_auths
        return int(bool(owner_auths) and owner_auths[0].account == raw.core_raw.name)

    def __check_for_recurrent_transfers(self, raw: UpdateNodeData._HarvestedData) -> int:
        assert raw.core_raw is not None  # mypy check

        return int(raw.core_raw.open_recurrent_transfers > 0)

    def __check_is_governance_is_expiring(self, raw: UpdateNodeData._HarvestedData) -> int:
        warning_period_in_days: Final[int] = 31

        assert raw.core_raw is not None  # mypy check

        return int(
            raw.core_raw.governance_vote_expiration_ts - timedelta(days=warning_period_in_days)
            > self.__normalize_datetime(datetime.utcnow())
        )

    def __get_account_reputation(self, raw: UpdateNodeData._HarvestedData) -> int:
        assert raw.core_raw is not None  # mypy check
        assert raw.reputation_raw is not None  # mypy check

        with SuppressNotExistingApi("reputation_api"):
            reputation = raw.reputation_raw.reputations
            assert len(reputation) == 1
            assert reputation[0].account == raw.core_raw.name, "reputation data malformed"
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

        dest.full_regeneration = self.__get_manabar_regeneration_time(
            gdpo_time=gdpo.time, max_mana=max_mana, current_mana=power_from_api, last_update_time=last_update
        )

    def __get_manabar_regeneration_time(
        self, gdpo_time: datetime, max_mana: int, current_mana: int, last_update_time: int
    ) -> timedelta:
        if max_mana <= 0:
            return timedelta(0)
        return (
            calculate_manabar_full_regeneration_time(
                now=int(gdpo_time.timestamp()),
                max_mana=max_mana,
                current_mana=current_mana,
                last_update_time=last_update_time,
            )
            - gdpo_time
        )

    def __vests_to_hive(self, amount: int | Asset.Vests, gdpo: DynamicGlobalPropertiesT) -> Asset.Hive:
        if isinstance(amount, Asset.Vests):
            amount = int(amount.amount)
        return Asset.Hive(
            amount=int(amount * int(gdpo.total_vesting_fund_hive.amount) / int(gdpo.total_vesting_shares.amount))
        )

    def __normalize_datetime(self, date: datetime) -> datetime:
        return date.replace(microsecond=0, tzinfo=timezone.utc)

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from math import ceil
from typing import TYPE_CHECKING, Final, cast

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.iwax import (
    calculate_current_manabar_value,
    calculate_manabar_full_regeneration_time,
)
from clive.__private.storage.accounts import Account
from clive.exceptions import CommunicationError
from clive.models import Asset
from clive.models.aliased import (
    DynamicGlobalProperties,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType

    from clive.__private.core.node.node import Node
    from clive.__private.storage import mock_database
    from clive.models.aliased import (
        ChangeRecoveryAccountRequest,
        DeclineVotingRightsRequest,
        FindRcAccounts,
        OwnerHistory,
        RcAccount,
        Reputation,
        SchemasAccount,
    )
    from schemas.apis.account_history_api import GetAccountHistory
    from schemas.apis.database_api import (
        FindAccounts,
        ListChangeRecoveryAccountRequests,
        ListDeclineVotingRightsRequests,
        ListOwnerHistories,
    )
    from schemas.apis.reputation_api import GetAccountReputations
    from schemas.fields.compound import Manabar


def _get_utc_epoch() -> datetime:
    return datetime.fromtimestamp(0, timezone.utc)


class SuppressNotExistingApis:
    _API_NOT_FOUND_REGEX: Final[str] = (
        r"'Assert Exception:api_itr != data\._registered_apis\.end\(\): Could not find API (\w+_api)'"
    )

    def __init__(self, *api_names: str) -> None:
        self.__api_names = api_names

    def __enter__(self) -> None:
        return None

    def __exit__(self, _: type[Exception] | None, error: Exception | None, __: TracebackType | None) -> bool:
        if isinstance(error, CommunicationError):
            apis_not_found = set(self.__get_apis_not_found(str(error)))
            not_suppressed_apis = apis_not_found - set(self.__api_names)
            return not bool(not_suppressed_apis)
        return False

    def __get_apis_not_found(self, message: str) -> list[str]:
        return re.findall(self._API_NOT_FOUND_REGEX, message)


@dataclass
class _AccountHarvestedDataRaw:
    core: SchemasAccount | None = None
    rc: RcAccount | None = None
    reputations: GetAccountReputations | None = None
    account_history: GetAccountHistory | None = None
    decline_voting_rights: ListDeclineVotingRightsRequests | None = None
    change_recovery_account_requests: ListChangeRecoveryAccountRequests | None = None
    owner_history: ListOwnerHistories | None = None


@dataclass
class _AccountSanitizedData:
    core: SchemasAccount
    decline_voting_rights: list[DeclineVotingRightsRequest]
    change_recovery_account_requests: list[ChangeRecoveryAccountRequest]
    owner_history: list[OwnerHistory]
    reputation: Reputation | None = None
    """Could be missing if reputation_api is not available"""
    account_history: GetAccountHistory | None = None
    """Could be missing if account_history_api is not available"""
    rc: RcAccount | None = None
    """Could be missing if rc_api is not available"""


@dataclass
class _AccountProcessedData:
    core: SchemasAccount
    warnings: int = 0
    reputation: int = 0
    """Could be missing if reputation_api is not available"""
    last_history_entry: datetime = field(default_factory=lambda: _get_utc_epoch())
    """Could be missing if account_history_api is not available"""
    rc: RcAccount | None = None
    """Could be missing if rc_api is not available"""


@dataclass
class HarvestedDataRaw:
    core_accounts: FindAccounts | None = None
    rc_accounts: FindRcAccounts | None = None
    account_harvested_data: dict[Account, _AccountHarvestedDataRaw] = field(
        default_factory=lambda: defaultdict(_AccountHarvestedDataRaw)
    )


AccountSanitizedDataContainer = dict[Account, _AccountSanitizedData]


@dataclass
class UpdateNodeData(CommandDataRetrieval[HarvestedDataRaw, AccountSanitizedDataContainer, DynamicGlobalProperties]):
    node: Node
    accounts: list[Account] = field(default_factory=list)

    async def _execute(self) -> None:
        self._result = await self.node.api.database_api.get_dynamic_global_properties()
        if not self.accounts:
            return

        await super()._execute()

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        non_virtual_operations_filter: Final[int] = 0x3FFFFFFFFFFFF
        account_names = [acc.name for acc in self.accounts if acc.name]
        harvested_data: HarvestedDataRaw = HarvestedDataRaw()

        async with self.node.batch(delay_error_on_data_access=True) as node:
            harvested_data.core_accounts = await node.api.database_api.find_accounts(accounts=account_names)
            harvested_data.rc_accounts = await node.api.rc_api.find_rc_accounts(accounts=account_names)

            account_harvested_data = harvested_data.account_harvested_data
            for account in self.accounts:
                account_harvested_data[account].reputations = await node.api.reputation_api.get_account_reputations(
                    account_lower_bound=account.name, limit=1
                )

                account_harvested_data[account].account_history = (
                    await node.api.account_history_api.get_account_history(
                        account=account.name,
                        limit=1,
                        operation_filter_low=non_virtual_operations_filter,
                        include_reversible=True,
                    )
                )

                account_harvested_data[account].decline_voting_rights = (
                    await node.api.database_api.list_decline_voting_rights_requests(
                        start=account.name, limit=1, order="by_account"
                    )
                )
                account_harvested_data[account].change_recovery_account_requests = (
                    await node.api.database_api.list_change_recovery_account_requests(
                        start=account.name, limit=1, order="by_account"
                    )
                )
                account_harvested_data[account].owner_history = await node.api.database_api.list_owner_histories(
                    start=(account.name, _get_utc_epoch()), limit=1
                )

        return harvested_data

    async def _sanitize_data(self, data: HarvestedDataRaw) -> AccountSanitizedDataContainer:
        for core_account in self.__assert_core_accounts(data.core_accounts):
            account = self.__get_account(core_account.name)
            data.account_harvested_data[account].core = core_account

        for rc_account in self.__assert_rc_accounts(data.rc_accounts):  # might be empty
            account = self.__get_account(rc_account.account)
            data.account_harvested_data[account].rc = rc_account

        sanitized: AccountSanitizedDataContainer = {}
        for account, unsanitized in data.account_harvested_data.items():
            sanitized[account] = _AccountSanitizedData(
                core=unsanitized.core,  # type:ignore[arg-type] # already sanitized above
                rc=unsanitized.rc,
                reputation=self.__assert_reputation_or_none(unsanitized.reputations, account.name),
                account_history=self.__assert_account_history_or_none(unsanitized.account_history),
                decline_voting_rights=self.__assert_declive_voting_rights(unsanitized.decline_voting_rights),
                change_recovery_account_requests=self.__assert_change_recovery_account_requests(
                    unsanitized.change_recovery_account_requests
                ),
                owner_history=self.__assert_owner_history(unsanitized.owner_history),
            )
        return sanitized

    async def _process_data(self, data: AccountSanitizedDataContainer) -> DynamicGlobalProperties:
        downvote_vote_ratio: Final[int] = 4

        gdpo = self.result

        accounts_processed_data: dict[Account, _AccountProcessedData] = {}
        for account in self.accounts:
            account_data = data[account]
            accounts_processed_data[account] = _AccountProcessedData(
                core=account_data.core,
                rc=account_data.rc,
                last_history_entry=self.__get_account_last_history_entry(account_data.account_history),
                warnings=self.__calculate_warnings(account_data),
                reputation=self.__get_account_reputation(account_data.reputation),
            )

        for account, info in accounts_processed_data.items():
            account.data.reputation = info.reputation
            account.data.last_history_entry = info.last_history_entry
            account.data.last_account_update = info.core.last_account_update
            account.data.warnings = info.warnings

            account.data.hive_balance = info.core.balance
            account.data.hbd_balance = info.core.hbd_balance
            account.data.hive_savings = info.core.savings_balance
            account.data.hbd_savings = info.core.savings_hbd_balance
            account.data.hive_unclaimed = info.core.reward_hive_balance
            account.data.hbd_unclaimed = info.core.reward_hbd_balance
            account.data.hp_unclaimed = info.core.reward_vesting_balance
            account.data.recovery_account = info.core.recovery_account

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
        return gdpo

    def __calculate_warnings(self, raw: _AccountSanitizedData) -> int:
        checks: list[Callable[[_AccountSanitizedData], bool]] = [
            self.__check_for_recurrent_transfers,
            self.__check_is_governance_is_expiring,
            self.__check_is_recovery_account_not_warning_listed,
            self.__check_is_declining_voting_rights_in_progress,
            self.__check_is_changing_recovery_account_is_in_progress,
            self.__check_is_owner_key_change_is_in_progress,
        ]
        return sum(check(raw) for check in checks)

    def __check_is_recovery_account_not_warning_listed(self, data: _AccountSanitizedData) -> bool:
        warning_recovery_accounts: Final[set[str]] = {"steem"}
        return data.core.recovery_account in warning_recovery_accounts

    def __check_is_declining_voting_rights_in_progress(self, data: _AccountSanitizedData) -> bool:
        requests = data.decline_voting_rights
        return bool(requests) and requests[0].account == data.core.name

    def __check_is_changing_recovery_account_is_in_progress(self, data: _AccountSanitizedData) -> bool:
        requests = data.change_recovery_account_requests
        return bool(requests) and requests[0].account_to_recover == data.core.name

    def __check_is_owner_key_change_is_in_progress(self, data: _AccountSanitizedData) -> bool:
        history = data.owner_history
        return bool(history) and history[0].account == data.core.name

    def __check_for_recurrent_transfers(self, data: _AccountSanitizedData) -> bool:
        return data.core.open_recurrent_transfers > 0

    def __check_is_governance_is_expiring(self, data: _AccountSanitizedData) -> bool:
        warning_period_in_days: Final[int] = 31
        return data.core.governance_vote_expiration_ts - timedelta(
            days=warning_period_in_days
        ) > self.__normalize_datetime(datetime.utcnow())

    def __get_account_reputation(self, data: Reputation | None) -> int:
        return 0 if data is None else int(data.reputation)

    def __get_account_last_history_entry(self, data: GetAccountHistory | None) -> datetime:
        if data is None:
            return _get_utc_epoch()
        return self.__normalize_datetime(data.history[0][1].timestamp)

    def __calculate_hive_power(
        self,
        gdpo: DynamicGlobalProperties,
        account: SchemasAccount,
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
        self, gdpo: DynamicGlobalProperties, max_mana: int, manabar: Manabar, dest: mock_database.Manabar
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

    def __vests_to_hive(self, amount: int | Asset.Vests, gdpo: DynamicGlobalProperties) -> Asset.Hive:
        if isinstance(amount, Asset.Vests):
            amount = int(amount.amount)
        return Asset.Hive(
            amount=int(amount * int(gdpo.total_vesting_fund_hive.amount) / int(gdpo.total_vesting_shares.amount))
        )

    @staticmethod
    def __normalize_datetime(date: datetime) -> datetime:
        return date.replace(microsecond=0, tzinfo=timezone.utc)

    def __get_account(self, name: str) -> Account:
        return next(filter(lambda account: account.name == name, self.accounts))

    def __assert_core_accounts(self, data: FindAccounts | None) -> list[SchemasAccount]:
        assert data is not None, "Core account data is missing..."
        assert len(data.accounts) == len(self.accounts), "Core accounts are missing some accounts..."
        return data.accounts

    def __assert_rc_accounts(self, data: FindRcAccounts | None) -> list[RcAccount]:
        assert data is not None, "Rc account data is missing..."

        with SuppressNotExistingApis("rc_api"):
            assert len(data.rc_accounts) == len(self.accounts), "RC accounts are missing some accounts..."
            return data.rc_accounts
        return []

    def __assert_reputation_or_none(self, data: GetAccountReputations | None, account_name: str) -> Reputation | None:
        assert data is not None, "Reputation data is missing..."

        with SuppressNotExistingApis("reputation_api"):
            reputations = data.reputations
            assert len(reputations) == 1, "Reputation data malformed. Expected only one entry."

            reputation = reputations[0]
            assert reputation.account == account_name, "Reputation data malformed. Account name mismatch."
            return reputation
        return None

    def __assert_account_history_or_none(self, data: GetAccountHistory | None) -> GetAccountHistory | None:
        assert data is not None, "Account history info is missing..."

        with SuppressNotExistingApis("account_history_api"):
            assert len(data.history) == 1, "Account history info malformed. Expected only one entry."
            return data
        return None

    def __assert_declive_voting_rights(
        self, decline_voting_rights: ListDeclineVotingRightsRequests | None
    ) -> list[DeclineVotingRightsRequest]:
        assert decline_voting_rights is not None, "Decline voting rights requests info is missing..."
        return decline_voting_rights.requests

    def __assert_change_recovery_account_requests(
        self, change_recovery_account_requests: ListChangeRecoveryAccountRequests | None
    ) -> list[ChangeRecoveryAccountRequest]:
        assert change_recovery_account_requests is not None, "Change recovery account requests info is missing..."
        return change_recovery_account_requests.requests

    def __assert_owner_history(self, owner_key_change_in_progress: ListOwnerHistories | None) -> list[OwnerHistory]:
        assert owner_key_change_in_progress is not None, "Owner history info is missing..."
        return owner_key_change_in_progress.owner_auths

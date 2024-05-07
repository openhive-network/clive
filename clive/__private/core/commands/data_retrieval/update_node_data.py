from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Final

from clive.__private.core.calcluate_hive_power import calculate_hive_power
from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.hive_vests_conversions import vests_to_hive
from clive.__private.core.iwax import (
    calculate_current_manabar_value,
    calculate_manabar_full_regeneration_time,
)
from clive.__private.storage import mock_database
from clive.__private.storage.accounts import Account
from clive.__private.storage.mock_database import DisabledAPI, NodeData
from clive.exceptions import CommunicationError
from clive.models.aliased import (
    DynamicGlobalProperties,
)

if TYPE_CHECKING:
    from types import TracebackType

    from clive.__private.core.node.node import Node
    from clive.models.aliased import (
        FindRcAccounts,
        RcAccount,
        SchemasAccount,
    )
    from schemas.apis.account_history_api import GetAccountHistory
    from schemas.apis.database_api import (
        FindAccounts,
    )
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

    def __exit__(self, _: type[BaseException] | None, error: BaseException | None, __: TracebackType | None) -> bool:
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
    account_history: GetAccountHistory | None = None


@dataclass
class _AccountSanitizedData:
    core: SchemasAccount
    account_history: GetAccountHistory | None = None
    """Could be missing if account_history_api is not available"""
    rc: RcAccount | None = None
    """Could be missing if rc_api is not available"""


@dataclass
class _AccountProcessedData:
    core: SchemasAccount
    last_history_entry: datetime = field(default_factory=lambda: _get_utc_epoch())
    """Could be missing if account_history_api is not available"""
    rc: RcAccount | None = None
    """Could be missing if rc_api is not available"""


@dataclass
class HarvestedDataRaw:
    gdpo: DynamicGlobalProperties | None = None
    core_accounts: FindAccounts | None = None
    rc_accounts: FindRcAccounts | None = None
    account_harvested_data: dict[Account, _AccountHarvestedDataRaw] = field(
        default_factory=lambda: defaultdict(_AccountHarvestedDataRaw)
    )


AccountSanitizedDataContainer = dict[Account, _AccountSanitizedData]


@dataclass
class SanitizedData:
    gdpo: DynamicGlobalProperties
    account_sanitized_data: AccountSanitizedDataContainer


@dataclass
class UpdateNodeData(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, DynamicGlobalProperties]):
    node: Node
    accounts: list[Account] = field(default_factory=list)

    async def _execute(self) -> None:
        self.__assert_no_duplicate_accounts()
        if not self.accounts:
            # We only need to fetch GDPO if no accounts were provided - otherwise it will be fetched in the same (batch)
            # query with other account-related data. Otherwise, if that would happen in a separate call we might get a
            # stale GDPO (for previous block).
            self._result = await self.node.api.database_api.get_dynamic_global_properties()
            return

        await super()._execute()

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        non_virtual_operations_filter: Final[int] = 0x3FFFFFFFFFFFF
        account_names = [acc.name for acc in self.accounts if acc.name]
        harvested_data: HarvestedDataRaw = HarvestedDataRaw()

        async with self.node.batch(delay_error_on_data_access=True) as node:
            harvested_data.gdpo = await node.api.database_api.get_dynamic_global_properties()
            harvested_data.core_accounts = await node.api.database_api.find_accounts(accounts=account_names)
            harvested_data.rc_accounts = await node.api.rc_api.find_rc_accounts(accounts=account_names)

            account_harvested_data = harvested_data.account_harvested_data
            for account in self.accounts:
                account_harvested_data[account].account_history = (
                    await node.api.account_history_api.get_account_history(
                        account=account.name,
                        limit=1,
                        operation_filter_low=non_virtual_operations_filter,
                        include_reversible=True,
                    )
                )

        return harvested_data

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        for core_account in self.__assert_core_accounts(data.core_accounts):
            account = self.__get_account(core_account.name)
            data.account_harvested_data[account].core = core_account

        for rc_account in self.__assert_rc_accounts(data.rc_accounts):  # might be empty
            account = self.__get_account(rc_account.account)
            data.account_harvested_data[account].rc = rc_account

        account_sanitized_data: AccountSanitizedDataContainer = {}
        for account, unsanitized in data.account_harvested_data.items():
            account_sanitized_data[account] = _AccountSanitizedData(
                core=unsanitized.core,  # type:ignore[arg-type] # already sanitized above
                rc=unsanitized.rc,
                account_history=self.__assert_account_history_or_none(unsanitized.account_history),
            )
        return SanitizedData(gdpo=self.__assert_gpdo(data.gdpo), account_sanitized_data=account_sanitized_data)

    async def _process_data(self, data: SanitizedData) -> DynamicGlobalProperties:
        downvote_vote_ratio: Final[int] = 4

        gdpo = data.gdpo

        accounts_processed_data: dict[Account, _AccountProcessedData] = {}
        for account in self.accounts:
            account_data = data.account_sanitized_data[account]
            accounts_processed_data[account] = _AccountProcessedData(
                core=account_data.core,
                rc=account_data.rc,
                last_history_entry=self.__get_account_last_history_entry(account_data.account_history),
            )

        for account, info in accounts_processed_data.items():
            account._data = NodeData(
                hbd_balance=info.core.hbd_balance,
                hbd_savings=info.core.savings_hbd_balance,
                hbd_unclaimed=info.core.reward_hbd_balance,
                hive_balance=info.core.balance,
                hive_savings=info.core.savings_balance,
                hive_unclaimed=info.core.reward_hive_balance,
                hp_balance=calculate_hive_power(gdpo, self._calculate_vests_balance(info.core)),
                proxy=info.core.proxy,
                hp_unclaimed=info.core.reward_vesting_balance,
                last_refresh=self.__normalize_datetime(datetime.utcnow()),
                last_history_entry=info.last_history_entry,
                last_account_update=info.core.last_account_update,
                recovery_account=info.core.recovery_account,
                vote_manabar=self.__update_manabar(
                    gdpo, int(info.core.post_voting_power.amount), info.core.voting_manabar
                ),
                downvote_manabar=self.__update_manabar(
                    gdpo, int(info.core.post_voting_power.amount) // downvote_vote_ratio, info.core.downvote_manabar
                ),
                rc_manabar=(
                    self.__update_manabar(gdpo, int(info.rc.max_rc), info.rc.rc_manabar)
                    if info.rc
                    else DisabledAPI(missing_api="rc_api")
                ),
            )

        return gdpo

    def __get_account_last_history_entry(self, data: GetAccountHistory | None) -> datetime:
        if data is None:
            return _get_utc_epoch()
        return self.__normalize_datetime(data.history[0][1].timestamp)

    def _calculate_vests_balance(self, account: SchemasAccount) -> int:
        return (
            int(account.vesting_shares.amount)
            - int(account.delegated_vesting_shares.amount)
            + int(account.received_vesting_shares.amount)
        )

    def __update_manabar(self, gdpo: DynamicGlobalProperties, max_mana: int, manabar: Manabar) -> mock_database.Manabar:
        power_from_api = int(manabar.current_mana)
        last_update = int(manabar.last_update_time)
        max_mana_value = vests_to_hive(max_mana, gdpo)
        mana_value = vests_to_hive(
            calculate_current_manabar_value(
                now=int(gdpo.time.timestamp()),
                max_mana=max_mana,
                current_mana=power_from_api,
                last_update_time=last_update,
            ),
            gdpo,
        )
        full_regeneration = self.__get_manabar_regeneration_time(
            gdpo_time=gdpo.time, max_mana=max_mana, current_mana=power_from_api, last_update_time=last_update
        )

        return mock_database.Manabar(
            value=mana_value,
            max_value=max_mana_value,
            full_regeneration=full_regeneration,
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

    @staticmethod
    def __normalize_datetime(date: datetime) -> datetime:
        return date.replace(microsecond=0, tzinfo=timezone.utc)

    def __get_account(self, name: str) -> Account:
        return next(filter(lambda account: account.name == name, self.accounts))

    def __assert_gpdo(self, data: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert data is not None, "GDPO data is missing..."
        return data

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

    def __assert_account_history_or_none(self, data: GetAccountHistory | None) -> GetAccountHistory | None:
        assert data is not None, "Account history info is missing..."

        with SuppressNotExistingApis("account_history_api"):
            assert len(data.history) == 1, "Account history info malformed. Expected only one entry."
            return data
        return None

    def __assert_no_duplicate_accounts(self) -> None:
        account_names = [account.name for account in self.accounts]
        message = f"Incorrect usage. Duplicate accounts provided: {account_names}..."
        assert len(account_names) == len(set(account_names)), message

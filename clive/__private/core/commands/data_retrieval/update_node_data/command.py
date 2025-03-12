from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Final

from beekeepy.interfaces import SuppressApiNotFound

from clive.__private.core import iwax
from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.core.commands.data_retrieval.update_node_data.models import Manabar, NodeData
from clive.__private.core.commands.data_retrieval.update_node_data.temporary_models import (
    AccountProcessedData,
    AccountSanitizedData,
    AccountSanitizedDataContainer,
    HarvestedDataRaw,
    SanitizedData,
)
from clive.__private.core.date_utils import utc_epoch, utc_now
from clive.__private.core.iwax import (
    calculate_current_manabar_value,
    calculate_manabar_full_regeneration_time,
)
from clive.__private.models.disabled_api import DisabledAPI
from clive.__private.models.hp_vests_balance import HpVestsBalance
from clive.__private.models.schemas import (
    DynamicGlobalProperties,
)

if TYPE_CHECKING:
    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.node import Node
    from clive.__private.models.schemas import (
        Account,
        FindAccounts,
        FindRcAccounts,
        GetAccountHistory,
        RcAccount,
    )
    from clive.__private.models.schemas import (
        Manabar as SchemasManabar,
    )


@dataclass
class UpdateNodeData(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, DynamicGlobalProperties]):
    node: Node
    accounts: list[TrackedAccount] = field(default_factory=list)

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

        async with await self.node.batch(delay_error_on_data_access=True) as node:
            harvested_data.gdpo = await node.api.database_api.get_dynamic_global_properties()
            harvested_data.core_accounts = await node.api.database_api.find_accounts(accounts=account_names)
            harvested_data.rc_accounts = await node.api.rc_api.find_rc_accounts(accounts=account_names)

            account_harvested_data = harvested_data.account_harvested_data
            for account in self.accounts:
                account_history = await node.api.account_history_api.get_account_history(
                    account=account.name,
                    limit=1,
                    operation_filter_low=non_virtual_operations_filter,
                    include_reversible=True,
                )

                account_harvested_data[account].account_history = account_history

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
            account_sanitized_data[account] = AccountSanitizedData(
                core=unsanitized.core,  # type:ignore[arg-type] # already sanitized above
                rc=unsanitized.rc,
                account_history=self.__assert_account_history_or_none(unsanitized.account_history),
            )
        return SanitizedData(gdpo=self.__assert_gpdo(data.gdpo), account_sanitized_data=account_sanitized_data)

    async def _process_data(self, data: SanitizedData) -> DynamicGlobalProperties:
        downvote_vote_ratio: Final[int] = 4

        gdpo = data.gdpo

        accounts_processed_data: dict[TrackedAccount, AccountProcessedData] = {}
        for account in self.accounts:
            account_data = data.account_sanitized_data[account]
            accounts_processed_data[account] = AccountProcessedData(
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
                owned_hp_balance=HpVestsBalance.create(info.core.vesting_shares, gdpo),
                unclaimed_hp_balance=HpVestsBalance.create(info.core.reward_vesting_balance, gdpo),
                proxy=info.core.proxy,
                last_refresh=utc_now(),
                last_history_entry=info.last_history_entry,
                last_account_update=info.core.last_account_update.value,
                pending_claimed_accounts=info.core.pending_claimed_accounts.value,
                recovery_account=info.core.recovery_account,
                governance_vote_expiration_ts=info.core.governance_vote_expiration_ts.value,
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
            return utc_epoch()
        return data.history[0][1].timestamp.value

    def __update_manabar(self, gdpo: DynamicGlobalProperties, max_mana: int, manabar: SchemasManabar) -> Manabar:
        head_block_time = gdpo.time
        head_block_timestamp = int(head_block_time.timestamp())
        last_update_timestamp = manabar.last_update_time.value
        power_from_api = manabar.current_mana.value
        max_mana_value = iwax.calculate_vests_to_hp(max_mana, gdpo)
        mana_value = iwax.calculate_vests_to_hp(
            calculate_current_manabar_value(
                now=head_block_timestamp,
                max_mana=max_mana,
                current_mana=power_from_api,
                last_update_time=last_update_timestamp,
            ),
            gdpo,
        )
        full_regeneration = self.__get_manabar_regeneration_time(
            head_block_time=head_block_time.value,
            max_mana=max_mana,
            current_mana=power_from_api,
            last_update_time=last_update_timestamp,
        )

        return Manabar(
            value=mana_value,
            max_value=max_mana_value,
            full_regeneration=full_regeneration,
        )

    def __get_manabar_regeneration_time(
        self, head_block_time: datetime, max_mana: int, current_mana: int, last_update_time: int
    ) -> timedelta:
        if max_mana <= 0:
            return timedelta(0)
        head_block_timestamp = int(head_block_time.timestamp())
        return (
            calculate_manabar_full_regeneration_time(
                now=head_block_timestamp,
                max_mana=max_mana,
                current_mana=current_mana,
                last_update_time=last_update_time,
            )
            - head_block_time
        )

    def __get_account(self, name: str) -> TrackedAccount:
        return next(filter(lambda account: account.name == name, self.accounts))

    def __assert_gpdo(self, data: DynamicGlobalProperties | None) -> DynamicGlobalProperties:
        assert data is not None, "GDPO data is missing..."
        return data

    def __assert_core_accounts(self, data: FindAccounts | None) -> list[Account]:
        assert data is not None, "Core account data is missing..."
        assert len(data.accounts) == len(self.accounts), "Core accounts are missing some accounts..."
        return data.accounts

    def __assert_rc_accounts(self, data: FindRcAccounts | None) -> list[RcAccount]:
        assert data is not None, "Rc account data is missing..."

        with SuppressApiNotFound("rc_api"):
            assert len(data.rc_accounts) == len(self.accounts), "RC accounts are missing some accounts..."
            return data.rc_accounts
        return []

    def __assert_account_history_or_none(self, data: GetAccountHistory | None) -> GetAccountHistory | None:
        assert data is not None, "Account history info is missing..."

        with SuppressApiNotFound("account_history_api"):
            assert len(data.history) == 1, "Account history info malformed. Expected only one entry."
            return data
        return None

    def __assert_no_duplicate_accounts(self) -> None:
        account_names = [account.name for account in self.accounts]
        message = f"Incorrect usage. Duplicate accounts provided: {account_names}..."
        assert len(account_names) == len(set(account_names)), message

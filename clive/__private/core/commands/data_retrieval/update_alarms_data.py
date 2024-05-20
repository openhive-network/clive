from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.storage.accounts import Account

if TYPE_CHECKING:
    from clive.__private.core.node import Node
    from clive.models.aliased import (
        ChangeRecoveryAccountRequest,
        DeclineVotingRightsRequest,
        OwnerHistory,
    )
    from schemas.apis.database_api import (
        ListChangeRecoveryAccountRequests,
        ListDeclineVotingRightsRequests,
        ListOwnerHistories,
    )


def _get_utc_epoch() -> datetime:
    return datetime.fromtimestamp(0, timezone.utc)


@dataclass
class _AccountAlarmsHarvestedDataRaw:
    decline_voting_rights: ListDeclineVotingRightsRequests | None = None
    change_recovery_account_requests: ListChangeRecoveryAccountRequests | None = None
    owner_history: ListOwnerHistories | None = None


@dataclass
class _AccountAlarmsSanitizedData:
    decline_voting_rights: list[DeclineVotingRightsRequest]
    change_recovery_account_request: (
        ChangeRecoveryAccountRequest | None
    )  # Can be None if there are no change recovery account requests for this account.
    owner_history: list[OwnerHistory]


@dataclass
class AccountAlarmsProcessedData:
    account_name: str
    recovery_account: str
    governance_vote_expiration_ts: datetime
    decline_voting_rights: list[DeclineVotingRightsRequest]
    change_recovery_account_request: ChangeRecoveryAccountRequest | None
    owner_history: list[OwnerHistory]


@dataclass
class HarvestedAlarmsDataRaw:
    account_harvested_data: dict[Account, _AccountAlarmsHarvestedDataRaw] = field(
        default_factory=lambda: defaultdict(_AccountAlarmsHarvestedDataRaw)
    )


AccountSanitizedAlarmsDataContainer = dict[Account, _AccountAlarmsSanitizedData]


@dataclass
class SanitizedAlarmsData:
    account_sanitized_data: AccountSanitizedAlarmsDataContainer


@dataclass(kw_only=True)
class UpdateAlarmsData(CommandDataRetrieval[HarvestedAlarmsDataRaw, SanitizedAlarmsData, None]):
    node: Node
    accounts: list[Account]

    async def _execute(self) -> None:
        if not self.accounts:
            return
        await super()._execute()

    async def _harvest_data_from_api(self) -> HarvestedAlarmsDataRaw:
        harvested_data: HarvestedAlarmsDataRaw = HarvestedAlarmsDataRaw()

        async with self.node.batch() as node:
            account_harvested_data = harvested_data.account_harvested_data
            for account in self.accounts:
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

    async def _sanitize_data(self, data: HarvestedAlarmsDataRaw) -> SanitizedAlarmsData:
        account_sanitized_data: AccountSanitizedAlarmsDataContainer = {}
        for account, unsanitized in data.account_harvested_data.items():
            account_sanitized_data[account] = _AccountAlarmsSanitizedData(
                decline_voting_rights=self._assert_declive_voting_rights(
                    unsanitized.decline_voting_rights, account.name
                ),
                change_recovery_account_request=self._assert_change_recovery_account_requests(
                    unsanitized.change_recovery_account_requests, account.name
                ),
                owner_history=self._assert_owner_history(unsanitized.owner_history),
            )
        return SanitizedAlarmsData(account_sanitized_data=account_sanitized_data)

    async def _process_data(self, data: SanitizedAlarmsData) -> None:
        accounts_processed_data: dict[Account, AccountAlarmsProcessedData] = {}
        for account in self.accounts:
            account_data = data.account_sanitized_data[account]
            accounts_processed_data[account] = AccountAlarmsProcessedData(
                account_name=account.name,
                recovery_account=account.data.recovery_account,
                governance_vote_expiration_ts=account.data.governance_vote_expiration_ts,
                decline_voting_rights=account_data.decline_voting_rights,
                change_recovery_account_request=account_data.change_recovery_account_request,
                owner_history=account_data.owner_history,
            )

        for account, info in accounts_processed_data.items():
            account._alarms.update_alarms_status(info)

    def _assert_declive_voting_rights(
        self, decline_voting_rights: ListDeclineVotingRightsRequests | None, account_name: str
    ) -> list[DeclineVotingRightsRequest]:
        assert decline_voting_rights is not None, "Decline voting rights requests info is missing..."
        return [request for request in decline_voting_rights.requests if request.account == account_name]

    def _assert_change_recovery_account_requests(
        self, change_recovery_account_requests: ListChangeRecoveryAccountRequests | None, account_name: str
    ) -> ChangeRecoveryAccountRequest | None:
        assert change_recovery_account_requests is not None, "Change recovery account requests info is missing..."
        requests = [
            request
            for request in change_recovery_account_requests.requests
            if request.account_to_recover == account_name
        ]
        if requests:
            assert len(requests) == 1, "Too many change recovery account requests for account."
            return requests[0]

        return None

    def _assert_owner_history(self, owner_key_change_in_progress: ListOwnerHistories | None) -> list[OwnerHistory]:
        assert owner_key_change_in_progress is not None, "Owner history info is missing..."
        return owner_key_change_in_progress.owner_auths

    def _get_account(self, name: str) -> Account:
        return next(filter(lambda account: account.name == name, self.accounts))

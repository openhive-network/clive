from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from clive.__private.core.accounts.accounts import TrackedAccount
from clive.__private.core.commands.abc.command_cached_data_retrieval import CommandCachedDataRetrieval

if TYPE_CHECKING:
    from clive.__private.core.node import Node
    from clive.__private.models.schemas import (
        ChangeRecoveryAccountRequest,
        DeclineVotingRightsRequest,
        ListChangeRecoveryAccountRequests,
        ListDeclineVotingRightsRequests,
    )


def _get_utc_epoch() -> datetime:
    return datetime.fromtimestamp(0, timezone.utc)


@dataclass
class _AccountAlarmsHarvestedData:
    decline_voting_rights: ListDeclineVotingRightsRequests
    change_recovery_account_requests: ListChangeRecoveryAccountRequests


@dataclass
class _AccountAlarmsSanitizedData:
    decline_voting_rights: DeclineVotingRightsRequest | None
    """Can be None if there is no change decline voting rights requests for this account."""
    change_recovery_account_request: ChangeRecoveryAccountRequest | None
    """Can be None if there is no change recovery account requests for this account."""


@dataclass
class AccountAlarmsData:
    account_name: str
    recovery_account: str
    governance_vote_expiration_ts: datetime
    decline_voting_rights: DeclineVotingRightsRequest | None
    """Can be None if there is no change decline voting rights requests for this account."""
    change_recovery_account_request: ChangeRecoveryAccountRequest | None
    """Can be None if there is no change recovery account requests for this account."""


AccountHarvestedAlarmsDataContainer = dict[TrackedAccount, _AccountAlarmsHarvestedData]
AccountSanitizedAlarmsDataContainer = dict[TrackedAccount, _AccountAlarmsSanitizedData]


@dataclass(kw_only=True)
class UpdateAlarmsData(
    CommandCachedDataRetrieval[AccountHarvestedAlarmsDataContainer, AccountSanitizedAlarmsDataContainer]
):
    node: Node
    accounts: list[TrackedAccount]

    async def _execute(self) -> None:
        if not self.accounts:
            return
        await super()._execute()

    async def _harvest_data_from_api(self) -> AccountHarvestedAlarmsDataContainer:
        accounts_data: AccountHarvestedAlarmsDataContainer = {}

        async with await self.node.batch() as node:
            for account in self.accounts:
                decline_voting_rights = await node.api.database_api.list_decline_voting_rights_requests(
                    start=account.name, limit=1, order="by_account"
                )

                change_recovery_account_requests = await node.api.database_api.list_change_recovery_account_requests(
                    start=account.name, limit=1, order="by_account"
                )

                accounts_data[account] = _AccountAlarmsHarvestedData(
                    decline_voting_rights, change_recovery_account_requests
                )

        return accounts_data

    async def _sanitize_data(self, data: AccountHarvestedAlarmsDataContainer) -> AccountSanitizedAlarmsDataContainer:
        account_sanitized_data: AccountSanitizedAlarmsDataContainer = {}
        for account, unsanitized in data.items():
            account_sanitized_data[account] = _AccountAlarmsSanitizedData(
                decline_voting_rights=self._sanitize_decline_voting_rights_requests(
                    unsanitized.decline_voting_rights, account.name
                ),
                change_recovery_account_request=self._sanitize_change_recovery_account_requests(
                    unsanitized.change_recovery_account_requests, account.name
                ),
            )
        return account_sanitized_data

    async def _process_data(self, data: AccountSanitizedAlarmsDataContainer) -> None:
        accounts_processed_data: dict[TrackedAccount, AccountAlarmsData] = {}
        for account in self.accounts:
            account_data = data[account]
            accounts_processed_data[account] = AccountAlarmsData(
                account_name=account.name,
                recovery_account=account.data.recovery_account,
                governance_vote_expiration_ts=account.data.governance_vote_expiration_ts,
                decline_voting_rights=account_data.decline_voting_rights,
                change_recovery_account_request=account_data.change_recovery_account_request,
            )

        for account, info in accounts_processed_data.items():
            account._alarms.update_alarms_status(info)

    def _sanitize_decline_voting_rights_requests(
        self, decline_voting_rights: ListDeclineVotingRightsRequests, account_name: str
    ) -> DeclineVotingRightsRequest | None:
        # Filter requests for the account because the API can return requests for other accounts.
        requests = [request for request in decline_voting_rights.requests if request.account == account_name]
        self._assert_decline_voting_rights_requests(requests, account_name)
        return requests[0] if requests else None

    def _assert_decline_voting_rights_requests(
        self, requests: list[DeclineVotingRightsRequest], account_name: str
    ) -> None:
        self._assert_max_one_request(requests, account_name)
        self._assert_account_name_matches_in_results(requests, account_name, "account")

    def _sanitize_change_recovery_account_requests(
        self, change_recovery_account_requests: ListChangeRecoveryAccountRequests, account_name: str
    ) -> ChangeRecoveryAccountRequest | None:
        # Filter requests for the account because the API can return requests for other accounts.
        requests = [
            request
            for request in change_recovery_account_requests.requests
            if request.account_to_recover == account_name
        ]
        self._assert_change_recovery_account_requests(requests, account_name)
        return requests[0] if requests else None

    def _assert_change_recovery_account_requests(
        self, requests: list[ChangeRecoveryAccountRequest], account_name: str
    ) -> None:
        self._assert_max_one_request(requests, account_name)
        self._assert_account_name_matches_in_results(requests, account_name, "account_to_recover")

    def _assert_max_one_request(self, requests: list[Any], account_name: str) -> None:
        requests_amount = len(requests)
        message = f"Account can have no requests or only one request. {account_name} has {requests_amount}."
        assert requests_amount <= 1, message

    def _assert_account_name_matches_in_results(
        self, results: list[Any], account_name: str, account_attribute_name: str
    ) -> None:
        for result in results:
            account_in_request = getattr(result, account_attribute_name)
            message = f"Account name in result {account_in_request} does not match {account_name}."
            assert account_in_request == account_name, message

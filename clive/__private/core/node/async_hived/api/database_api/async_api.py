from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import Literal

from beekeepy.handle.remote import AbstractAsyncApi

from clive.__private.core.node.async_hived.api.database_api.common import DatabaseApiCommons
from hiveio_api import Asset, database_api
from hiveio_api.operations import Transaction


class DatabaseApi(AbstractAsyncApi, DatabaseApiCommons):
    api = AbstractAsyncApi.endpoint_jsonrpc

    @api
    async def find_account_recovery_requests(
        self, *, accounts: list[str]
    ) -> database_api.FindAccountRecoveryRequestsResponse:
        raise NotImplementedError

    @api
    async def find_accounts(
        self, *, accounts: list[str], delayed_votes_active: bool | None = None
    ) -> database_api.FindAccountsResponse:
        raise NotImplementedError

    @api
    async def find_change_recovery_account_requests(
        self, *, accounts: list[str]
    ) -> database_api.FindChangeRecoveryAccountRequestsResponse:
        raise NotImplementedError

    @api
    async def find_collateralized_conversion_requests(
        self, *, account: str
    ) -> database_api.FindCollateralizedConversionRequestsResponse:
        raise NotImplementedError

    @api
    async def find_comments(self, *, comments: list[tuple[str, str]]) -> database_api.FindCommentsResponse:
        raise NotImplementedError

    @api
    async def find_decline_voting_rights_requests(
        self, *, accounts: list[str]
    ) -> database_api.FindDeclineVotingRightsRequestsResponse:
        raise NotImplementedError

    @api
    async def find_escrows(self, *, from_: str = "") -> database_api.FindEscrowsResponse:
        raise NotImplementedError

    @api
    async def find_hbd_conversion_requests(self, *, account: str) -> database_api.FindHbdConversionRequestsResponse:
        raise NotImplementedError

    @api
    async def find_limit_orders(self, *, account: str) -> database_api.FindLimitOrdersResponse:
        raise NotImplementedError

    @api
    async def find_owner_histories(self, *, owner: str = "") -> database_api.FindOwnerHistoriesResponse:
        raise NotImplementedError

    @api
    async def find_proposals(self, *, proposal_ids: list[int]) -> database_api.FindProposalsResponse:
        raise NotImplementedError

    @api
    async def find_recurrent_transfers(self, *, from_: str = "") -> database_api.FindRecurrentTransfersResponse:
        raise NotImplementedError

    @api
    async def find_savings_withdrawals(self, *, account: str) -> database_api.FindSavingsWithdrawalsResponse:
        raise NotImplementedError

    @api
    async def find_vesting_delegation_expirations(
        self, *, account: str
    ) -> database_api.FindVestingDelegationExpirationsResponse:
        raise NotImplementedError

    @api
    async def find_vesting_delegations(self, *, account: str) -> database_api.FindVestingDelegationsResponse:
        raise NotImplementedError

    @api
    async def find_withdraw_vesting_routes(
        self, *, account: str, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.FindWithdrawVestingRoutesResponse:
        raise NotImplementedError

    @api
    async def find_witnesses(self, *, owners: list[str]) -> database_api.FindWitnessesResponse:
        raise NotImplementedError

    @api
    async def get_active_witnesses(self, *, include_future: bool = False) -> database_api.GetActiveWitnessesResponse:
        raise NotImplementedError

    @api
    async def get_comment_pending_payouts(
        self, *, comments: list[tuple[str, str]]
    ) -> database_api.GetCommentPendingPayoutsResponse:
        raise NotImplementedError

    @api
    async def get_config(self) -> database_api.GetConfigResponse:
        raise NotImplementedError

    @api
    async def get_current_price_feed(self) -> database_api.GetCurrentPriceFeedResponse:
        raise NotImplementedError

    @api
    async def get_dynamic_global_properties(
        self,
    ) -> database_api.GetDynamicGlobalPropertiesResponse:
        raise NotImplementedError

    @api
    async def get_feed_history(self) -> database_api.GetFeedHistoryResponse:
        raise NotImplementedError

    @api
    async def get_hardfork_properties(self) -> database_api.GetHardforkPropertiesResponse:
        raise NotImplementedError

    @api
    async def get_order_book(self, *, limit: int, base: Asset, quote: Asset) -> database_api.GetOrderBookResponse:
        raise NotImplementedError

    @api
    async def get_potential_signatures(self, *, trx: Transaction) -> database_api.GetPotentialSignaturesResponse:
        raise NotImplementedError

    @api
    async def get_required_signatures(self, *, trx: Transaction) -> database_api.GetPotentialSignaturesResponse:
        # Both get_required_signatures and get_potential_signatures share the same response schema in OpenAPI spec
        raise NotImplementedError

    @api
    async def get_reward_funds(self) -> database_api.GetRewardFundsResponse:
        raise NotImplementedError

    @api
    async def get_transaction_hex(self, *, trx: Transaction) -> database_api.GetTransactionHexResponse:
        raise NotImplementedError

    @api
    async def get_version(self) -> database_api.GetVersionResponse:
        raise NotImplementedError

    @api
    async def get_witness_schedule(self) -> database_api.GetWitnessScheduleResponse:
        raise NotImplementedError

    @api
    async def is_known_transaction(self, *, id_: str) -> database_api.IsKnownTransactionResponse:
        raise NotImplementedError

    @api
    async def list_account_recovery_requests(
        self, *, account: str, limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListAccountRecoveryRequestsResponse:
        raise NotImplementedError

    @api
    async def list_accounts(
        self,
        *,
        start: str | tuple[str, str] | tuple[datetime, str],
        limit: int,
        order: DatabaseApiCommons.SORT_TYPES,
        delayed_votes_active: bool = True,
    ) -> database_api.ListAccountsResponse:
        raise NotImplementedError

    @api
    async def list_change_recovery_account_requests(
        self, *, start: str | tuple[datetime, str], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListChangeRecoveryAccountRequestsResponse:
        raise NotImplementedError

    @api
    async def list_collateralized_conversion_requests(
        self, *, start: str | None, limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListCollateralizedConversionRequestsResponse:
        raise NotImplementedError

    @api
    async def list_decline_voting_rights_requests(
        self, *, start: str | tuple[datetime, str], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListDeclineVotingRightsRequestsResponse:
        raise NotImplementedError

    @api
    async def list_escrows(
        self, *, start: tuple[str, int] | tuple[bool, datetime, int], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListEscrowsResponse:
        raise NotImplementedError

    @api
    async def list_hbd_conversion_requests(
        self, *, limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListHbdConversionRequestsResponse:
        raise NotImplementedError

    @api
    async def list_limit_orders(
        self, *, start: tuple[str, int] | tuple[dict[Literal["base", "quote"], Asset], int]
    ) -> database_api.ListLimitOrdersResponse:
        raise NotImplementedError

    @api
    async def list_owner_histories(
        self, *, start: tuple[str, datetime], limit: int
    ) -> database_api.ListOwnerHistoriesResponse:
        raise NotImplementedError

    @api
    async def list_proposal_votes(
        self,
        *,
        start: list[str],
        limit: int,
        order: DatabaseApiCommons.SORT_TYPES,
        order_direction: DatabaseApiCommons.SORT_DIRECTION,
        status: DatabaseApiCommons.PROPOSAL_STATUS,
    ) -> database_api.ListProposalVotesResponse:
        raise NotImplementedError

    @api
    async def list_proposals(
        self,
        *,
        start: list[str] | list[int] | list[datetime],
        limit: int,
        order: DatabaseApiCommons.SORT_TYPES,
        order_direction: DatabaseApiCommons.SORT_DIRECTION,
        status: DatabaseApiCommons.PROPOSAL_STATUS,
    ) -> database_api.ListProposalsResponse:
        raise NotImplementedError

    @api
    async def list_savings_withdrawals(
        self,
        *,
        start: tuple[int] | tuple[datetime, str, int] | tuple[str, datetime, int],
        limit: int,
        order: DatabaseApiCommons.SORT_TYPES,
    ) -> database_api.ListSavingsWithdrawalsResponse:
        raise NotImplementedError

    @api
    async def list_vesting_delegation_expirations(
        self,
        *,
        start: tuple[str, datetime, int] | tuple[datetime, int],
        limit: int,
        order: DatabaseApiCommons.SORT_TYPES,
    ) -> database_api.ListVestingDelegationExpirationsResponse:
        raise NotImplementedError

    @api
    async def list_vesting_delegations(
        self, *, start: tuple[str, str], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListVestingDelegationsResponse:
        raise NotImplementedError

    @api
    async def list_withdraw_vesting_routes(
        self, *, start: tuple[str, str] | tuple[str, int], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListWithdrawVestingRoutesResponse:
        raise NotImplementedError

    @api
    async def list_witness_votes(
        self, *, start: tuple[str, str], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListWitnessVotesResponse:
        raise NotImplementedError

    @api
    async def list_witnesses(
        self, *, start: str | tuple[int, str] | tuple[str | int, str], limit: int, order: DatabaseApiCommons.SORT_TYPES
    ) -> database_api.ListWitnessesResponse:
        raise NotImplementedError

    @api
    async def verify_account_authority(
        self, *, account: str, signers: list[str]
    ) -> database_api.VerifyAccountAuthorityResponse:
        raise NotImplementedError

    @api
    async def verify_authority(
        self, *, trx: Transaction, pack: DatabaseApiCommons.PACK_TYPES = "hf26"
    ) -> database_api.VerifyAuthorityResponse:
        raise NotImplementedError

    @api
    async def verify_signatures(
        self,
        *,
        hash_: str,
        signatures: list[str],
        required_owner: list[str],
        required_active: list[str],
        required_posting: list[str],
        required_other: list[str],
    ) -> database_api.VerifySignaturesResponse:
        raise NotImplementedError

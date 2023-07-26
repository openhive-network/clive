from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from typing import Literal

from clive.__private.core.node.api.api import Api
from clive.models import Asset, Transaction  # noqa: TCH001
from schemas import database_api  # noqa: TCH001


class DatabaseApi(Api):
    PACK_TYPES = Literal["legacy", "hf26"]
    PROPOSAL_STATUS = Literal["all", "inactive", "active", "expired", "votable"]
    SORT_DIRECTION = Literal["ascending", "descending"]
    SORT_TYPES = Literal[
        "by_name",
        "by_proxy",
        "by_next_vesting_withdrawal",
        "by_account",
        "by_expiration",
        "by_effective_date",
        "by_vote_name",
        "by_schedule_time",
        "by_account_witness",
        "by_witness_account",
        "by_from_id",
        "by_ratification_deadline",
        "by_withdraw_route",
        "by_destination",
        "by_complete_from_id",
        "by_to_complete",
        "by_delegation",
        "by_account_expiration",
        "by_conversion_date",
        "by_cashout_time",
        "by_permlink",
        "by_parent",
        "by_comment_voter",
        "by_voter_comment",
        "by_price",
        "by_symbol_contributor",
        "by_symbol",
        "by_control_account",
        "by_symbol_time",
        "by_creator",
        "by_start_date",
        "by_end_date",
        "by_total_votes",
        "by_voter_proposal",
        "by_proposal_voter",
        "by_contributor",
        "by_symbol_id",
        "not_set",
    ]

    @Api.method
    async def find_account_recovery_requests(self, accounts: list[str]) -> database_api.FindAccountRecoveryRequests:
        raise NotImplementedError

    @Api.method
    async def find_accounts(
        self, accounts: list[str], delayed_votes_active: bool | None = None
    ) -> database_api.FindAccounts:
        raise NotImplementedError

    @Api.method
    async def find_change_recovery_account_requests(
        self, accounts: list[str]
    ) -> database_api.FindChangeRecoveryAccountRequests:
        raise NotImplementedError

    @Api.method
    async def find_collateralized_conversion_requests(
        self, account: str
    ) -> database_api.FindCollateralizedConversionRequests:
        raise NotImplementedError

    @Api.method
    async def find_comments(self, comments: list[tuple[str, str]]) -> database_api.FindComments:
        raise NotImplementedError

    @Api.method
    async def find_decline_voting_rights_requests(
        self, accounts: list[str]
    ) -> database_api.FindDeclineVotingRightsRequests:
        raise NotImplementedError

    @Api.method
    async def find_escrows(self, from_: str = "") -> database_api.FindEscrows:
        raise NotImplementedError

    @Api.method
    async def find_hbd_conversion_requests(self, account: str) -> database_api.FindHbdConversionRequests:
        raise NotImplementedError

    @Api.method
    async def find_limit_orders(self, account: str) -> database_api.FindLimitOrders:
        raise NotImplementedError

    @Api.method
    async def find_owner_histories(self, owner: str = "") -> database_api.FindOwnerHistories:
        raise NotImplementedError

    @Api.method
    async def find_proposals(self, proposal_ids: list[int]) -> database_api.FindProposals:
        raise NotImplementedError

    @Api.method
    async def find_recurrent_transfers(self, from_: str = "") -> database_api.FindRecurrentTransfers:
        raise NotImplementedError

    @Api.method
    async def find_savings_withdrawals(self, account: str) -> database_api.FindSavingsWithdrawals:
        raise NotImplementedError

    @Api.method
    async def find_vesting_delegation_expirations(self, account: str) -> database_api.FindVestingDelegationExpirations:
        raise NotImplementedError

    @Api.method
    async def find_vesting_delegations(self, account: str) -> database_api.FindVestingDelegations:
        raise NotImplementedError

    @Api.method
    async def find_withdraw_vesting_routes(
        self, account: str, order: DatabaseApi.SORT_TYPES
    ) -> database_api.FindWithdrawVestingRoutes:
        raise NotImplementedError

    @Api.method
    async def find_witnesses(self, owners: list[str]) -> database_api.FindWitnesses:
        raise NotImplementedError

    @Api.method
    async def get_active_witnesses(self) -> database_api.GetActiveWitnesses:
        raise NotImplementedError

    @Api.method
    async def get_comment_pending_payouts(
        self, comments: list[tuple[str, str]]
    ) -> database_api.GetCommentPendingPayouts:
        raise NotImplementedError

    @Api.method
    async def get_config(self) -> database_api.GetConfig[Asset.Hive, Asset.Hbd]:
        raise NotImplementedError

    @Api.method
    async def get_current_price_feed(self) -> database_api.GetCurrentPriceFeed:
        raise NotImplementedError

    @Api.method
    async def get_dynamic_global_properties(
        self,
    ) -> database_api.GetDynamicGlobalProperties[Asset.Hive, Asset.Hbd, Asset.Vests]:
        raise NotImplementedError

    @Api.method
    async def get_feed_history(self) -> database_api.GetFeedHistory[Asset.Hive, Asset.Hbd]:
        raise NotImplementedError

    @Api.method
    async def get_hardfork_properties(self) -> database_api.GetHardforkProperties:
        raise NotImplementedError

    @Api.method
    async def get_order_book(self, limit: int, base: Asset.Hive, quote: Asset.Hbd) -> database_api.GetOrderBook:
        raise NotImplementedError

    @Api.method
    async def get_potential_signatures(self, trx: Transaction) -> database_api.GetPotentialSignatures:
        raise NotImplementedError

    @Api.method
    async def get_required_signatures(self, trx: Transaction) -> database_api.GetRequiredSignatures:
        raise NotImplementedError

    @Api.method
    async def get_reward_funds(self) -> database_api.GetRewardFunds:
        raise NotImplementedError

    @Api.method
    async def get_transaction_hex(self, trx: Transaction) -> database_api.GetTransactionHex:
        raise NotImplementedError

    @Api.method
    async def get_version(self) -> database_api.GetVersion:
        raise NotImplementedError

    @Api.method
    async def get_witness_schedule(self) -> database_api.GetWitnessSchedule[Asset.Hive]:
        raise NotImplementedError

    @Api.method
    async def is_known_transaction(self, id_: str) -> database_api.IsKnownTransaction:
        raise NotImplementedError

    @Api.method
    async def list_account_recovery_requests(
        self, account: str, limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListAccountRecoveryRequests:
        raise NotImplementedError

    @Api.method
    async def list_accounts(
        self,
        start: str | tuple[str, str] | tuple[datetime, str],
        limit: int,
        order: DatabaseApi.SORT_TYPES,
        delayed_votes_active: bool = True,
    ) -> database_api.ListAccounts:
        raise NotImplementedError

    @Api.method
    async def list_change_recovery_account_requests(
        self, start: str | tuple[datetime, str], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListChangeRecoveryAccountRequests:
        raise NotImplementedError

    @Api.method
    async def list_collateralized_conversion_requests(
        self, start: str | None, limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListCollateralizedConversionRequests:
        raise NotImplementedError

    @Api.method
    async def list_decline_voting_rights_requests(
        self, start: str | tuple[datetime, str], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListDeclineVotingRightsRequests:
        raise NotImplementedError

    @Api.method
    async def list_escrows(
        self, start: tuple[str, int] | tuple[bool, datetime, int], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListEscrows:
        raise NotImplementedError

    @Api.method
    async def list_hbd_conversion_requests(
        self, limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListHbdConversionRequests:
        raise NotImplementedError

    @Api.method
    async def list_limit_orders(
        self, start: tuple[str, int] | tuple[dict[Literal["base", "quote"], Asset.Hive | Asset.Hbd], int]
    ) -> database_api.ListLimitOrders:
        raise NotImplementedError

    @Api.method
    async def list_owner_histories(self, start: tuple[str, datetime], limit: int) -> database_api.ListOwnerHistories:
        raise NotImplementedError

    @Api.method
    async def list_proposal_votes(  # noqa: PLR0913
        self,
        start: list[str],
        limit: int,
        order: DatabaseApi.SORT_TYPES,
        order_direction: DatabaseApi.SORT_DIRECTION,
        status: DatabaseApi.PROPOSAL_STATUS,
    ) -> database_api.ListProposalVotes:
        raise NotImplementedError

    @Api.method
    async def list_proposals(  # noqa: PLR0913
        self,
        start: list[str] | list[int] | list[datetime],
        limit: int,
        order: DatabaseApi.SORT_TYPES,
        order_direction: DatabaseApi.SORT_DIRECTION,
        status: DatabaseApi.PROPOSAL_STATUS,
    ) -> database_api.ListProposals:
        raise NotImplementedError

    @Api.method
    async def list_savings_withdrawals(
        self,
        start: tuple[int] | tuple[datetime, str, int] | tuple[str, datetime, int],
        limit: int,
        order: DatabaseApi.SORT_TYPES,
    ) -> database_api.ListSavingsWithdrawals:
        raise NotImplementedError

    @Api.method
    async def list_vesting_delegation_expirations(
        self, start: tuple[str, datetime, int] | tuple[datetime, int], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListVestingDelegationExpirations:
        raise NotImplementedError

    @Api.method
    async def list_vesting_delegations(
        self, start: tuple[str, str], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListVestingDelegations:
        raise NotImplementedError

    @Api.method
    async def list_withdraw_vesting_routes(
        self, start: tuple[str, str] | tuple[str, int], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListWithdrawVestingRoutes:
        raise NotImplementedError

    @Api.method
    async def list_witness_votes(
        self, start: tuple[str, str], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListWitnessVotes:
        raise NotImplementedError

    @Api.method
    async def list_witnesses(
        self, start: str | tuple[int, str] | tuple[str | int, str], limit: int, order: DatabaseApi.SORT_TYPES
    ) -> database_api.ListWitnesses:
        raise NotImplementedError

    @Api.method
    async def verify_account_authority(self, account: str, signers: list[str]) -> database_api.VerifyAccountAuthority:
        raise NotImplementedError

    @Api.method
    async def verify_authority(
        self, trx: Transaction, pack: DatabaseApi.PACK_TYPES = "hf26"
    ) -> database_api.VerifyAuthority:
        raise NotImplementedError

    @Api.method
    async def verify_signatures(  # noqa: PLR0913
        self,
        hash_: str,
        signatures: list[str],
        required_owner: list[str],
        required_active: list[str],
        required_posting: list[str],
        required_other: list[str],
    ) -> database_api.VerifySignatures:
        raise NotImplementedError

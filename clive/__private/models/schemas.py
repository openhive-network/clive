"""
Some of the models imported from hiveio_api and schemas should have a corresponding alias there.

If name matches our naming convention, no need to alias, just export in __all__.

Why this module exists?
* we want to have a single source of truth for API models (there are complicated ones requiring specialization),
* generated models are not always well named, and we want to have a consistent naming convention in our codebase,
* some imports from hiveio_api are very long,
* if something gets changed in hiveio_api, we'll have a single place to update aliases.

E.g. VestingDelegationExpiration = VestingDelegationExpirations has the name of the list of the API response.

Models of API responses, operations and transactions come from hiveio_api - dataclasses built without validation.
Field types come from schemas in the variant clive needs them:
* `AccountName`, `ChainId`, `TransactionId` - user-friendly types (`schemas.fields.user_friendly`) which validate values
  when created (e.g. `AccountName("alice")`) - use them with `is_matching_model` to validate input of users,
* the other ones - builtin aliases (`schemas.fields.public`, e.g. `PublicKey = str`) for annotations, as fields of the
  models of hiveio_api are annotated. Where such a type is needed at runtime (e.g. `Uint16t.meta()`), its user-friendly
  variant is imported from `schemas.fields.user_friendly`, fields of hand-written msgspec models take the forms of
  `schemas.fields.validation`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from hiveio_api._utilities.smart_lazy_import import aggregate_same_import, lazy_module_factory

__all__ = [  # noqa: RUF022
    # operation BASIC aliases
    "OperationBase",
    "OperationRepresentationUnion",
    "OperationUnion",
    # list API responses (have nested list property which stores actual model)
    "ListChangeRecoveryAccountRequests",
    "ListDeclineVotingRightsRequests",
    "ListProposals",
    "ListProposalVotes",
    "ListWitnesses",
    "ListWitnessVotes",
    "ListRcDirectDelegations",
    "ListWithdrawVestingRoutes",
    # find API response aliases (have nested list property which stores actual model)
    "FindAccounts",
    "FindProposals",
    "FindRcAccounts",
    "FindRecurrentTransfers",
    "FindSavingsWithdrawals",
    "FindVestingDelegationExpirations",
    "FindVestingDelegations",
    "FindWitnesses",
    # get API responses (have unnecessary nested property which stores actual model)
    "GetAccountHistory",
    "GetTransaction",
    # get API responses (have no unnecessary nested  properties, just the model itself)
    "Config",
    "DynamicGlobalProperties",
    "FeedHistory",
    "HardforkProperties",
    "Version",
    "WitnessSchedule",
    # operations
    "AccountCreateOperation",
    "AccountCreateWithDelegationOperation",
    "AccountUpdate2Operation",
    "AccountUpdateOperation",
    "AccountWitnessProxyOperation",
    "AccountWitnessVoteOperation",
    "CancelTransferFromSavingsOperation",
    "ChangeRecoveryAccountOperation",
    "ClaimAccountOperation",
    "ClaimRewardBalanceOperation",
    "CollateralizedConvertOperation",
    "CommentOperation",
    "CommentOptionsOperation",
    "ConvertOperation",
    "CreateClaimedAccountOperation",
    "CreateProposalOperation",
    "CustomBinaryOperation",
    "CustomJsonOperation",
    "CustomOperation",
    "DeclineVotingRightsOperation",
    "DelegateVestingSharesOperation",
    "DeleteCommentOperation",
    "EscrowApproveOperation",
    "EscrowDisputeOperation",
    "EscrowReleaseOperation",
    "EscrowTransferOperation",
    "FeedPublishOperation",
    "LimitOrderCancelOperation",
    "LimitOrderCreate2Operation",
    "LimitOrderCreateOperation",
    "Pow2Operation",
    "PowOperation",
    "RecoverAccountOperation",
    "RecurrentTransferOperation",
    "RemoveProposalOperation",
    "RequestAccountRecoveryOperation",
    "ResetAccountOperation",
    "SetResetAccountOperation",
    "SetWithdrawVestingRouteOperation",
    "TransferFromSavingsOperation",
    "TransferOperation",
    "TransferToSavingsOperation",
    "TransferToVestingOperation",
    "UpdateProposalOperation",
    "UpdateProposalVotesOperation",
    "VoteOperation",
    "WithdrawVestingOperation",
    "WitnessBlockApproveOperation",
    "WitnessSetPropertiesOperation",
    "WitnessUpdateOperation",
    # extensions
    "RecurrentTransferPairIdExtension",
    "RecurrentTransferPairIdRepresentation",
    # assets
    "AssetHbd",
    "AssetHive",
    # basic fields
    "AccountName",
    "ChainId",
    "Hex",
    "HiveDateTime",
    "HiveInt",
    "JsonString",
    "PublicKey",
    "Signature",
    "TransactionId",
    "Uint16t",
    "Uint32t",
    # compound models
    "Account",
    "Authority",
    "ChangeRecoveryAccountRequest",
    "DeclineVotingRightsRequest",
    "HbdExchangeRate",
    "LegacyChainProperties",
    "Manabar",
    "PriceFeed",
    "Proposal",
    "RcAccount",
    "RcDirectDelegation",
    "RecurrentTransfer",
    "SavingsWithdrawal",
    "Transaction",
    "TransactionStatus",
    "VestingDelegation",
    "VestingDelegationExpiration",
    "WithdrawRoute",
    "Witness",
    # other
    "PreconfiguredBaseModel",
    "convert_to_representation",
    "is_matching_model",
    "field",
]

if TYPE_CHECKING:
    from hiveio_api import HiveDateTime
    from hiveio_api.account_history_api import GetAccountHistoryResponse as GetAccountHistory
    from hiveio_api.account_history_api import GetTransactionResponse as GetTransaction
    from hiveio_api.database_api import (
        Account,
        DeclineVotingRights,
        FindAccountRecovery,
        GetConfigResponse,
        GetDynamicGlobalPropertiesResponse,
        GetFeedHistoryResponse,
        GetHardforkPropertiesResponse,
        GetVersionResponse,
        GetWitnessScheduleResponse,
        Proposals,
        RecurrentTransfer,
        SavingsWithdrawal,
        VestingDelegation,
        VestingDelegationExpirations,
        VotingManabar,
        WithdrawVestingRoutes,
        Witness,
    )
    from hiveio_api.database_api import FindAccountsResponse as FindAccounts
    from hiveio_api.database_api import FindProposalsResponse as FindProposals
    from hiveio_api.database_api import FindRecurrentTransfersResponse as FindRecurrentTransfers
    from hiveio_api.database_api import FindSavingsWithdrawalsResponse as FindSavingsWithdrawals
    from hiveio_api.database_api import FindVestingDelegationExpirationsResponse as FindVestingDelegationExpirations
    from hiveio_api.database_api import FindVestingDelegationsResponse as FindVestingDelegations
    from hiveio_api.database_api import FindWitnessesResponse as FindWitnesses
    from hiveio_api.database_api import ListChangeRecoveryAccountRequestsResponse as ListChangeRecoveryAccountRequests
    from hiveio_api.database_api import ListDeclineVotingRightsRequestsResponse as ListDeclineVotingRightsRequests
    from hiveio_api.database_api import ListProposalsResponse as ListProposals
    from hiveio_api.database_api import ListProposalVotesResponse as ListProposalVotes
    from hiveio_api.database_api import ListWithdrawVestingRoutesResponse as ListWithdrawVestingRoutes
    from hiveio_api.database_api import ListWitnessesResponse as ListWitnesses
    from hiveio_api.database_api import ListWitnessVotesResponse as ListWitnessVotes
    from hiveio_api.operations import (
        AccountCreateOperation,
        AccountCreateWithDelegationOperation,
        AccountUpdate2Operation,
        AccountUpdateOperation,
        AccountWitnessProxyOperation,
        AccountWitnessVoteOperation,
        Authority,
        CancelTransferFromSavingsOperation,
        ChangeRecoveryAccountOperation,
        ClaimAccountOperation,
        ClaimRewardBalanceOperation,
        CollateralizedConvertOperation,
        CommentOperation,
        CommentOptionsOperation,
        ConvertOperation,
        CreateClaimedAccountOperation,
        CreateProposalOperation,
        CustomBinaryOperation,
        CustomJsonOperation,
        CustomOperation,
        DeclineVotingRightsOperation,
        DelegateVestingSharesOperation,
        DeleteCommentOperation,
        EscrowApproveOperation,
        EscrowDisputeOperation,
        EscrowReleaseOperation,
        EscrowTransferOperation,
        FeedPublishOperation,
        Hf26Operation,
        Hf26OperationValue,
        Hf26RecurrentTransferPairId,
        LegacyChainProperties,
        LimitOrderCancelOperation,
        LimitOrderCreate2Operation,
        LimitOrderCreateOperation,
        OperationBase,
        Pow2Operation,
        PowOperation,
        Price,
        RecoverAccountOperation,
        RecurrentTransferOperation,
        RecurrentTransferPairId,
        RemoveProposalOperation,
        RequestAccountRecoveryOperation,
        ResetAccountOperation,
        SetResetAccountOperation,
        SetWithdrawVestingRouteOperation,
        Transaction,
        TransferFromSavingsOperation,
        TransferOperation,
        TransferToSavingsOperation,
        TransferToVestingOperation,
        UpdateProposalOperation,
        UpdateProposalVotesOperation,
        VoteOperation,
        WithdrawVestingOperation,
        WitnessBlockApproveOperation,
        WitnessSetPropertiesOperation,
        WitnessUpdateOperation,
    )
    from hiveio_api.operations import hf26_operation as convert_to_representation
    from hiveio_api.rc_api import FindRcAccountsResponse as FindRcAccounts
    from hiveio_api.rc_api import ListRcDirectDelegationsResponse as ListRcDirectDelegations
    from hiveio_api.rc_api import RcAccount, RcAccountDelegation
    from hiveio_api.transaction_status_api import FindTransactionResponse as TransactionStatus
    from schemas._preconfigured_base_model import PreconfiguredBaseModel
    from schemas.base import field
    from schemas.fields.public import (
        AssetHbd,
        AssetHive,
        Hex,
        HiveInt,
        JsonString,
        PublicKey,
        Signature,
        Uint16t,
        Uint32t,
    )
    from schemas.fields.user_friendly import AccountName, Sha256, TransactionId
    from schemas.validation import is_matching_model

    # operation BASIC aliases

    OperationRepresentationUnion = Hf26Operation
    OperationUnion = Hf26OperationValue

    # get API responses (have no unnecessary nested  properties, just the model itself)

    Config = GetConfigResponse
    DynamicGlobalProperties = GetDynamicGlobalPropertiesResponse
    FeedHistory = GetFeedHistoryResponse
    HardforkProperties = GetHardforkPropertiesResponse
    Version = GetVersionResponse
    WitnessSchedule = GetWitnessScheduleResponse

    # extensions

    RecurrentTransferPairIdExtension = RecurrentTransferPairId
    RecurrentTransferPairIdRepresentation = Hf26RecurrentTransferPairId

    # basic fields

    ChainId = Sha256

    # compound models

    ChangeRecoveryAccountRequest = FindAccountRecovery
    DeclineVotingRightsRequest = DeclineVotingRights
    HbdExchangeRate = Price
    Manabar = VotingManabar
    PriceFeed = Price
    Proposal = Proposals
    RcDirectDelegation = RcAccountDelegation
    VestingDelegationExpiration = VestingDelegationExpirations
    WithdrawRoute = WithdrawVestingRoutes

lazy_getattr = lazy_module_factory(
    globals(),
    *aggregate_same_import(
        ("FindAccountsResponse", "FindAccounts"),
        ("FindProposalsResponse", "FindProposals"),
        ("FindRecurrentTransfersResponse", "FindRecurrentTransfers"),
        ("FindSavingsWithdrawalsResponse", "FindSavingsWithdrawals"),
        ("FindVestingDelegationExpirationsResponse", "FindVestingDelegationExpirations"),
        ("FindVestingDelegationsResponse", "FindVestingDelegations"),
        ("FindWitnessesResponse", "FindWitnesses"),
        ("ListChangeRecoveryAccountRequestsResponse", "ListChangeRecoveryAccountRequests"),
        ("ListDeclineVotingRightsRequestsResponse", "ListDeclineVotingRightsRequests"),
        ("ListProposalsResponse", "ListProposals"),
        ("ListProposalVotesResponse", "ListProposalVotes"),
        ("ListWithdrawVestingRoutesResponse", "ListWithdrawVestingRoutes"),
        ("ListWitnessesResponse", "ListWitnesses"),
        ("ListWitnessVotesResponse", "ListWitnessVotes"),
        ("GetConfigResponse", "Config"),
        ("GetDynamicGlobalPropertiesResponse", "DynamicGlobalProperties"),
        ("GetFeedHistoryResponse", "FeedHistory"),
        ("GetHardforkPropertiesResponse", "HardforkProperties"),
        ("GetVersionResponse", "Version"),
        ("GetWitnessScheduleResponse", "WitnessSchedule"),
        "Account",
        ("DeclineVotingRights", "DeclineVotingRightsRequest"),
        ("FindAccountRecovery", "ChangeRecoveryAccountRequest"),
        ("Proposals", "Proposal"),
        "RecurrentTransfer",
        "SavingsWithdrawal",
        "VestingDelegation",
        ("VestingDelegationExpirations", "VestingDelegationExpiration"),
        ("VotingManabar", "Manabar"),
        ("WithdrawVestingRoutes", "WithdrawRoute"),
        "Witness",
        module="hiveio_api.database_api",
    ),
    *aggregate_same_import(
        "AccountCreateOperation",
        "AccountCreateWithDelegationOperation",
        "AccountUpdate2Operation",
        "AccountUpdateOperation",
        "AccountWitnessProxyOperation",
        "AccountWitnessVoteOperation",
        "CancelTransferFromSavingsOperation",
        "ChangeRecoveryAccountOperation",
        "ClaimAccountOperation",
        "ClaimRewardBalanceOperation",
        "CollateralizedConvertOperation",
        "CommentOperation",
        "CommentOptionsOperation",
        ("hf26_operation", "convert_to_representation"),
        "ConvertOperation",
        "CreateClaimedAccountOperation",
        "CreateProposalOperation",
        "CustomBinaryOperation",
        "CustomJsonOperation",
        "CustomOperation",
        "DeclineVotingRightsOperation",
        "DelegateVestingSharesOperation",
        "DeleteCommentOperation",
        "EscrowApproveOperation",
        "EscrowDisputeOperation",
        "EscrowReleaseOperation",
        "EscrowTransferOperation",
        "FeedPublishOperation",
        "LimitOrderCancelOperation",
        "LimitOrderCreate2Operation",
        "LimitOrderCreateOperation",
        "Pow2Operation",
        "PowOperation",
        "RecoverAccountOperation",
        "RecurrentTransferOperation",
        "RemoveProposalOperation",
        "RequestAccountRecoveryOperation",
        "ResetAccountOperation",
        "SetResetAccountOperation",
        "SetWithdrawVestingRouteOperation",
        "TransferFromSavingsOperation",
        "TransferOperation",
        "TransferToSavingsOperation",
        "TransferToVestingOperation",
        "UpdateProposalOperation",
        "UpdateProposalVotesOperation",
        "VoteOperation",
        "WithdrawVestingOperation",
        "WitnessBlockApproveOperation",
        "WitnessSetPropertiesOperation",
        "WitnessUpdateOperation",
        "Authority",
        "LegacyChainProperties",
        ("Price", "PriceFeed"),
        ("Price", "HbdExchangeRate"),
        ("Hf26Operation", "OperationRepresentationUnion"),
        ("Hf26OperationValue", "OperationUnion"),
        "OperationBase",
        ("Hf26RecurrentTransferPairId", "RecurrentTransferPairIdRepresentation"),
        "Transaction",
        ("RecurrentTransferPairId", "RecurrentTransferPairIdExtension"),
        module="hiveio_api.operations",
    ),
    *aggregate_same_import(
        "AssetHbd",
        "AssetHive",
        "Hex",
        "HiveInt",
        "JsonString",
        "PublicKey",
        "Signature",
        "Uint16t",
        "Uint32t",
        module="schemas.fields.public",
    ),
    *aggregate_same_import(
        "AccountName",
        ("Sha256", "ChainId"),
        "TransactionId",
        module="schemas.fields.user_friendly",
    ),
    *aggregate_same_import(
        ("FindRcAccountsResponse", "FindRcAccounts"),
        ("ListRcDirectDelegationsResponse", "ListRcDirectDelegations"),
        "RcAccount",
        ("RcAccountDelegation", "RcDirectDelegation"),
        module="hiveio_api.rc_api",
    ),
    *aggregate_same_import(
        ("GetAccountHistoryResponse", "GetAccountHistory"),
        ("GetTransactionResponse", "GetTransaction"),
        module="hiveio_api.account_history_api",
    ),
    ("hiveio_api.transaction_status_api", "FindTransactionResponse", "TransactionStatus"),
    ("hiveio_api", "HiveDateTime"),
    ("schemas.base", "field"),
    ("schemas.validation", "is_matching_model"),
    ("schemas._preconfigured_base_model", "PreconfiguredBaseModel"),
)

if not TYPE_CHECKING:
    __getattr__ = lazy_getattr

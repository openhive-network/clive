"""
Some of the models imported from schemas should have a corresponding alias there.

If name matches our naming convention, no need to alias, just export in __all__.

Why this module exists?
* we want to have a single source of truth for schema models (there are complicated ones requiring specialization),
* schemas are not always well named, and we want to have a consistent naming convention in our codebase,
* some models and not specialized with HF26 assets,
* some imports from schemas are very long,
* if something gets changed in schemas, we'll have a single place to update aliases.

E.g. VestingDelegationExpiration = VestingDelegationExpirationsFundament[AssetVestsHF26]
has unnecessary "Fundament" suffix, and is not specialized with HF26 assets.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

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
    "AssetVests",
    # basic fields
    "AccountName",
    "ChainId",
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
    "Manabar",
    "PriceFeed",
    "Proposal",
    "RcAccount",
    "RecurrentTransfer",
    "SavingsWithdrawal",
    "Transaction",
    "TransactionStatus",
    "VestingDelegation",
    "VestingDelegationExpiration",
    "WithdrawRoute",
    "Witness",
    # policies
    "ExtraFieldsPolicy",
    "MissingFieldsInGetConfigPolicy",
    "TestnetAssetsPolicy",
    "set_policies",
    # exceptions
    "DecodeError",
    "ValidationError",
    # other
    "PreconfiguredBaseModel",
    "convert_to_representation",
    "is_matching_model",
    "validate_schema_field",
    "field",
]

if TYPE_CHECKING:
    from schemas._preconfigured_base_model import PreconfiguredBaseModel
    from schemas.apis.account_history_api import GetAccountHistory
    from schemas.apis.database_api import (
        FindAccounts,
        FindProposals,
        FindRecurrentTransfers,
        FindSavingsWithdrawals,
        FindVestingDelegationExpirations,
        FindVestingDelegations,
        FindWitnesses,
        GetConfig,
        GetDynamicGlobalProperties,
        GetFeedHistory,
        GetHardforkProperties,
        GetVersion,
        GetWitnessSchedule,
        ListChangeRecoveryAccountRequests,
        ListDeclineVotingRightsRequests,
        ListProposals,
        ListProposalVotes,
        ListWithdrawVestingRoutes,
        ListWitnesses,
        ListWitnessVotes,
    )
    from schemas.apis.database_api.fundaments_of_reponses import (
        AccountItemFundament,
        FindRecurrentTransfersFundament,
        ListChangeRecoveryAccountRequestsFundament,
        ListDeclineVotingRightsRequestsFundament,
        SavingsWithdrawalsFundament,
        VestingDelegationExpirationsFundament,
        VestingDelegationsFundament,
        WithdrawVestingRoutesFundament,
        WitnessesFundament,
    )
    from schemas.apis.rc_api import FindRcAccounts
    from schemas.apis.rc_api.fundaments_of_responses import RcAccount
    from schemas.apis.transaction_status_api import FindTransaction
    from schemas.base import field
    from schemas.decoders import is_matching_model, validate_schema_field
    from schemas.errors import DecodeError, ValidationError
    from schemas.fields.assets import AssetHbd, AssetHive, AssetVests
    from schemas.fields.basic import AccountName, PublicKey
    from schemas.fields.compound import Authority, HbdExchangeRate, Manabar, Price, Proposal
    from schemas.fields.hex import Sha256, Signature, TransactionId
    from schemas.fields.hive_datetime import HiveDateTime
    from schemas.fields.hive_int import HiveInt
    from schemas.fields.integers import Uint16t, Uint32t
    from schemas.fields.resolvables import JsonString
    from schemas.operation import Operation
    from schemas.operations import (
        AccountCreateOperation,
        AccountCreateWithDelegationOperation,
        AccountUpdate2Operation,
        AccountUpdateOperation,
        AccountWitnessProxyOperation,
        AccountWitnessVoteOperation,
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
        Hf26OperationRepresentation,
        Hf26Operations,
        LimitOrderCancelOperation,
        LimitOrderCreate2Operation,
        LimitOrderCreateOperation,
        Pow2Operation,
        PowOperation,
        RecoverAccountOperation,
        RemoveProposalOperation,
        RequestAccountRecoveryOperation,
        ResetAccountOperation,
        SetResetAccountOperation,
        SetWithdrawVestingRouteOperation,
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
        convert_to_representation,
    )
    from schemas.operations.extensions.recurrent_transfer_extensions import RecurrentTransferPairId
    from schemas.operations.extensions.representation_types import (
        HF26RepresentationRecurrentTransferPairIdOperationExtension,
    )
    from schemas.operations.recurrent_transfer_operation import RecurrentTransferOperation
    from schemas.policies import (
        ExtraFieldsPolicy,
        MissingFieldsInGetConfigPolicy,
        TestnetAssetsPolicy,
        set_policies,
    )
    from schemas.transaction import Transaction

    # operation BASIC aliases

    OperationBase = Operation
    OperationRepresentationUnion = Hf26OperationRepresentation
    OperationUnion = Hf26Operations

    # get API responses (have no unnecessary nested  properties, just the model itself)

    Config = GetConfig
    DynamicGlobalProperties = GetDynamicGlobalProperties
    FeedHistory = GetFeedHistory
    HardforkProperties = GetHardforkProperties
    Version = GetVersion
    WitnessSchedule = GetWitnessSchedule

    # extensions

    RecurrentTransferPairIdExtension = RecurrentTransferPairId
    RecurrentTransferPairIdRepresentation = HF26RepresentationRecurrentTransferPairIdOperationExtension

    # basic fields

    ChainId = Sha256

    # compound models

    Account = AccountItemFundament
    ChangeRecoveryAccountRequest = ListChangeRecoveryAccountRequestsFundament
    DeclineVotingRightsRequest = ListDeclineVotingRightsRequestsFundament
    PriceFeed = Price
    RecurrentTransfer = FindRecurrentTransfersFundament
    SavingsWithdrawal = SavingsWithdrawalsFundament
    TransactionStatus = FindTransaction
    VestingDelegation = VestingDelegationsFundament
    VestingDelegationExpiration = VestingDelegationExpirationsFundament
    WithdrawRoute = WithdrawVestingRoutesFundament
    Witness = WitnessesFundament
else:
    from beekeepy._utilities.smart_lazy_import import aggregate_same_import, lazy_module_factory

    __getattr__ = lazy_module_factory(
        globals(),
        **aggregate_same_import(
            "FindAccounts",
            "FindProposals",
            "FindRecurrentTransfers",
            "FindSavingsWithdrawals",
            "FindVestingDelegationExpirations",
            "FindVestingDelegations",
            "FindWitnesses",
            "ListChangeRecoveryAccountRequests",
            "ListDeclineVotingRightsRequests",
            "ListProposals",
            "ListProposalVotes",
            "ListWithdrawVestingRoutes",
            "ListWitnesses",
            "ListWitnessVotes",
            ("GetConfig", "Config"),
            ("GetDynamicGlobalProperties", "DynamicGlobalProperties"),
            ("GetFeedHistory", "FeedHistory"),
            ("GetHardforkProperties", "HardforkProperties"),
            ("GetVersion", "Version"),
            ("GetWitnessSchedule", "WitnessSchedule"),
            module="schemas.apis.database_api",
        ),
        **aggregate_same_import(
            ("AccountItemFundament", "Account"),
            ("FindRecurrentTransfersFundament", "RecurrentTransfer"),
            ("ListChangeRecoveryAccountRequestsFundament", "ChangeRecoveryAccountRequest"),
            ("ListDeclineVotingRightsRequestsFundament", "DeclineVotingRightsRequest"),
            ("SavingsWithdrawalsFundament", "SavingsWithdrawal"),
            ("VestingDelegationExpirationsFundament", "VestingDelegationExpiration"),
            ("VestingDelegationsFundament", "VestingDelegation"),
            ("WithdrawVestingRoutesFundament", "WithdrawRoute"),
            ("WitnessesFundament", "Witness"),
            module="schemas.apis.database_api.fundaments_of_reponses",
        ),
        **aggregate_same_import(
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
            "convert_to_representation",
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
            ("Hf26OperationRepresentation", "OperationRepresentationUnion"),
            ("Hf26Operations", "OperationUnion"),
            module="schemas.operations",
        ),
        **aggregate_same_import(
            "ExtraFieldsPolicy",
            "MissingFieldsInGetConfigPolicy",
            "set_policies",
            "TestnetAssetsPolicy",
            module="schemas.policies",
        ),
        **aggregate_same_import(
            "AssetHbd",
            "AssetHive",
            "AssetVests",
            module="schemas.fields.assets",
        ),
        **aggregate_same_import(
            "Authority",
            "Manabar",
            ("Price", "PriceFeed"),
            module="schemas.fields.compound",
        ),
        **aggregate_same_import(
            "Signature",
            "TransactionId",
            ("Sha256", "ChainId"),
            module="schemas.fields.hex",
        ),
        **aggregate_same_import(
            "Uint16t",
            "Uint32t",
            module="schemas.fields.integers",
        ),
        **aggregate_same_import(
            "AccountName",
            "PublicKey",
            module="schemas.fields.basic",
        ),
        **aggregate_same_import(
            "is_matching_model",
            "validate_schema_field",
            module="schemas.decoders",
        ),
        **aggregate_same_import(
            "DecodeError",
            "ValidationError",
            module="schemas.errors",
        ),
        **aggregate_same_import(
            "HbdExchangeRate",
            "Proposal",
            module="schemas.fields.compound",
        ),
        field="schemas.base",
        FindRcAccounts="schemas.apis.rc_api",
        FindTransaction=("schemas.apis.transaction_status_api", "TransactionStatus"),
        GetAccountHistory="schemas.apis.account_history_api",
        HF26RepresentationRecurrentTransferPairIdOperationExtension=(
            "schemas.operations.extensions.representation_types",
            "RecurrentTransferPairIdRepresentation",
        ),
        HiveDateTime="schemas.fields.hive_datetime",
        HiveInt="schemas.fields.hive_int",
        JsonString="schemas.fields.resolvables",
        Operation=("schemas.operation", "OperationBase"),
        PreconfiguredBaseModel="schemas._preconfigured_base_model",
        RcAccount="schemas.apis.rc_api.fundaments_of_responses",
        RecurrentTransferOperation="schemas.operations.recurrent_transfer_operation",
        RecurrentTransferPairId=(
            "schemas.operations.extensions.recurrent_transfer_extensions",
            "RecurrentTransferPairIdExtension",
        ),
        Transaction="schemas.transaction",
    )

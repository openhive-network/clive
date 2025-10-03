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
    from sys import modules

    from beekeepy._utilities.smart_lazy_import import aggregate_same_import, lazy_module_factory

    __getattr__ = lazy_module_factory(
        modules[__name__],
        __all__,
        aliases={
            "OperationBase": "Operation",
            "OperationRepresentationUnion": "Hf26OperationRepresentation",
            "OperationUnion": "Hf26Operations",
            "Config": "GetConfig",
            "DynamicGlobalProperties": "GetDynamicGlobalProperties",
            "FeedHistory": "GetFeedHistory",
            "HardforkProperties": "GetHardforkProperties",
            "Version": "GetVersion",
            "WitnessSchedule": "GetWitnessSchedule",
            "RecurrentTransferPairIdExtension": "RecurrentTransferPairId",
            "RecurrentTransferPairIdRepresentation": "HF26RepresentationRecurrentTransferPairIdOperationExtension",
            "ChainId": "Sha256",
            "Account": "AccountItemFundament",
            "ChangeRecoveryAccountRequest": "ListChangeRecoveryAccountRequestsFundament",
            "DeclineVotingRightsRequest": "ListDeclineVotingRightsRequestsFundament",
            "PriceFeed": "Price",
            "RecurrentTransfer": "FindRecurrentTransfersFundament",
            "SavingsWithdrawal": "SavingsWithdrawalsFundament",
            "TransactionStatus": "FindTransaction",
            "VestingDelegation": "VestingDelegationsFundament",
            "VestingDelegationExpiration": "VestingDelegationExpirationsFundament",
            "WithdrawRoute": "WithdrawVestingRoutesFundament",
            "Witness": "WitnessesFundament",
        },
        **aggregate_same_import(
            "FindAccounts",
            "FindProposals",
            "FindRecurrentTransfers",
            "FindSavingsWithdrawals",
            "FindVestingDelegationExpirations",
            "FindVestingDelegations",
            "FindWitnesses",
            "GetConfig",
            "GetDynamicGlobalProperties",
            "GetFeedHistory",
            "GetHardforkProperties",
            "GetVersion",
            "GetWitnessSchedule",
            "ListChangeRecoveryAccountRequests",
            "ListDeclineVotingRightsRequests",
            "ListProposals",
            "ListProposalVotes",
            "ListWithdrawVestingRoutes",
            "ListWitnesses",
            "ListWitnessVotes",
            module="schemas.apis.database_api",
        ),
        **aggregate_same_import(
            "AccountItemFundament",
            "FindRecurrentTransfersFundament",
            "ListChangeRecoveryAccountRequestsFundament",
            "ListDeclineVotingRightsRequestsFundament",
            "SavingsWithdrawalsFundament",
            "VestingDelegationExpirationsFundament",
            "VestingDelegationsFundament",
            "WithdrawVestingRoutesFundament",
            "WitnessesFundament",
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
            "Hf26OperationRepresentation",
            "Hf26Operations",
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
            "convert_to_representation",
            module="schemas.operations",
        ),
        **aggregate_same_import(
            "ExtraFieldsPolicy",
            "MissingFieldsInGetConfigPolicy",
            "TestnetAssetsPolicy",
            "set_policies",
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
            "Price",
            module="schemas.fields.compound",
        ),
        **aggregate_same_import(
            "Sha256",
            "Signature",
            "TransactionId",
            module="schemas.fields.hex",
        ),
        FindTransaction="schemas.apis.transaction_status_api",
        field="schemas.base",
        is_matching_model="schemas.decoders",
        validate_schema_field="schemas.decoders",
        DecodeError="schemas.errors",
        ValidationError="schemas.errors",
        AccountName="schemas.fields.basic",
        PublicKey="schemas.fields.basic",
        HiveDateTime="schemas.fields.hive_datetime",
        HiveInt="schemas.fields.hive_int",
        Uint16t="schemas.fields.integers",
        Uint32t="schemas.fields.integers",
        JsonString="schemas.fields.resolvables",
        Operation="schemas.operation",
        RecurrentTransferPairId="schemas.operations.extensions.recurrent_transfer_extensions",
        HF26RepresentationRecurrentTransferPairIdOperationExtension="schemas.operations.extensions.representation_types",
        RecurrentTransferOperation="schemas.operations.recurrent_transfer_operation",
        Transaction="schemas.transaction",
        PreconfiguredBaseModel="schemas._preconfigured_base_model",
        GetAccountHistory="schemas.apis.account_history_api",
        FindRcAccounts="schemas.apis.rc_api",
        RcAccount="schemas.apis.rc_api.fundaments_of_responses",
        HbdExchangeRate="schemas.fields.compound",
        Proposal="schemas.fields.compound",
    )

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

from schemas._operation_objects import Hf26ApiOperationObject
from schemas._preconfigured_base_model import PreconfiguredBaseModel
from schemas.apis.account_history_api import EnumVirtualOps, GetAccountHistory, GetOpsInBlock
from schemas.apis.account_history_api.response_schemas import GetTransaction
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
    OwnerHistoriesFundament,
    SavingsWithdrawalsFundament,
    VestingDelegationExpirationsFundament,
    VestingDelegationsFundament,
    WithdrawVestingRoutesFundament,
    WitnessesFundament,
)
from schemas.apis.rc_api import FindRcAccounts as SchemasFindRcAccounts
from schemas.apis.rc_api import GetResourceParams, GetResourcePool, ListRcDirectDelegations
from schemas.apis.rc_api import ListRcAccounts as SchemasListRcAccounts
from schemas.apis.rc_api.fundaments_of_responses import RcAccount as SchemasRcAccount
from schemas.apis.reputation_api import GetAccountReputations
from schemas.apis.transaction_status_api import FindTransaction
from schemas.decoders import is_matching_model, validate_schema_field
from schemas.fields.assets import AssetHbd, AssetHive, AssetVests
from schemas.fields.assets._base import AssetBase
from schemas.fields.basic import AccountName, PublicKey
from schemas.fields.compound import Authority, Manabar, Price
from schemas.fields.compound import HbdExchangeRate as SchemasHbdExchangeRate
from schemas.fields.compound import Proposal as SchemasProposal
from schemas.fields.hex import Sha256, Signature, TransactionId
from schemas.fields.hive_datetime import HiveDateTime
from schemas.fields.hive_int import HiveInt
from schemas.fields.resolvables import JsonString
from schemas.jsonrpc import ExpectResultT as JSONRPCExpectResultT
from schemas.jsonrpc import JSONRPCResult
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
    Policy,
    TestnetAssetsPolicy,
    set_policies,
)
from schemas.transaction import Transaction

__all__ = [  # noqa: RUF022
    # operation BASIC aliases
    "ApiOperationObject",
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
    "GetAccountReputations",
    "GetOperationsInBlock",
    "GetResourcePool",
    # get API responses (have no unnecessary nested  properties, just the model itself)
    "Config",
    "DynamicGlobalProperties",
    "FeedHistory",
    "HardforkProperties",
    "ResourceParams",
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
    "AssetBase",
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
    # compound models
    "Account",
    "Authority",
    "ChangeRecoveryAccountRequest",
    "DeclineVotingRightsRequest",
    "EnumeratedVirtualOperations",
    "HbdExchangeRate",
    "Manabar",
    "OwnerHistory",
    "PriceFeed",
    "Proposal",
    "RcAccount",
    "RecurrentTransfer",
    "SavingsWithdrawal",
    "Transaction",
    "TransactionInBlockchain",
    "TransactionStatus",
    "VestingDelegation",
    "VestingDelegationExpiration",
    "WithdrawRoute",
    "Witness",
    # policies
    "ExtraFieldsPolicy",
    "JSONRPCExpectResultT",
    "JSONRPCResult",
    "MissingFieldsInGetConfigPolicy",
    "Policy",
    "TestnetAssetsPolicy",
    "set_policies",
    # other
    "PreconfiguredBaseModel",
    "convert_to_representation",
    "is_matching_model",
    "validate_schema_field",
]

# operation BASIC aliases
ApiOperationObject = Hf26ApiOperationObject
OperationBase = Operation
OperationRepresentationUnion = Hf26OperationRepresentation
OperationUnion = Hf26Operations

#  list API responses (have nested list property which stores actual model)

ListRcAccounts = SchemasListRcAccounts

# find API response aliases (have nested list property which stores actual model)

FindRcAccounts = SchemasFindRcAccounts

# get API responses (have unnecessary nested property which stores actual model)

GetOperationsInBlock = GetOpsInBlock

# get API responses (have no unnecessary nested  properties, just the model itself)

Config = GetConfig
DynamicGlobalProperties = GetDynamicGlobalProperties
FeedHistory = GetFeedHistory
HardforkProperties = GetHardforkProperties
ResourceParams = GetResourceParams
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
EnumeratedVirtualOperations = EnumVirtualOps
HbdExchangeRate = SchemasHbdExchangeRate
OwnerHistory = OwnerHistoriesFundament
PriceFeed = Price
Proposal = SchemasProposal
RcAccount = SchemasRcAccount
RecurrentTransfer = FindRecurrentTransfersFundament
SavingsWithdrawal = SavingsWithdrawalsFundament
TransactionInBlockchain = GetTransaction
TransactionStatus = FindTransaction
VestingDelegation = VestingDelegationsFundament
VestingDelegationExpiration = VestingDelegationExpirationsFundament
WithdrawRoute = WithdrawVestingRoutesFundament
Witness = WitnessesFundament

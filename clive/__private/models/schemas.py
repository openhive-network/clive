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
from schemas.apis.rc_api import FindRcAccounts as SchemasFindRcAccounts
from schemas.apis.rc_api.fundaments_of_responses import RcAccount as SchemasRcAccount
from schemas.apis.transaction_status_api import FindTransaction
from schemas.fields.assets import AssetHbdHF26, AssetHiveHF26, AssetVestsHF26
from schemas.fields.basic import AccountName, PublicKey
from schemas.fields.compound import Authority, Manabar, Price
from schemas.fields.compound import HbdExchangeRate as SchemasHbdExchangeRate
from schemas.fields.compound import Proposal as SchemasProposal
from schemas.fields.hex import Sha256, Signature, TransactionId
from schemas.fields.hive_datetime import HiveDateTime
from schemas.fields.hive_int import HiveInt
from schemas.fields.serializable import Serializable
from schemas.operation import Operation
from schemas.operations import (
    AccountCreateOperation,
    AccountCreateWithDelegationOperation,
    AccountUpdate2Operation,
    AccountUpdateOperation,
    AccountWitnessProxyOperation,
    AccountWitnessVoteOperation,
    AnyOperation,
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
)
from schemas.operations.extensions.recurrent_transfer_extensions import RecurrentTransferPairId
from schemas.operations.recurrent_transfer_operation import RecurrentTransferOperation
from schemas.operations.representation_types import Hf26OperationRepresentationType
from schemas.operations.representations import convert_to_representation
from schemas.operations.representations.hf26_representation import HF26Representation
from schemas.policies import ExtraFields, MissingFieldsInGetConfig, Policy, set_policies
from schemas.transaction import Transaction

__all__ = [  # noqa: RUF022
    # operation BASIC aliases
    "OperationBase",
    "OperationRepresentationBase",
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
    "AssetHbdHF26",
    "AssetHiveHF26",
    "AssetVestsHF26",
    # basic fields
    "AccountName",
    "ChainId",
    "HiveDateTime",
    "HiveInt",
    "PublicKey",
    "Signature",
    "TransactionId",
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
    "Policy",
    "set_policies",
    # other
    "convert_to_representation",
    "RepresentationBase",
    "Serializable",
]

# operation BASIC aliases

OperationBase = Operation
OperationRepresentationBase = HF26Representation[OperationBase]
OperationRepresentationUnion = Hf26OperationRepresentationType
OperationUnion = AnyOperation

# find API response aliases (have nested list property which stores actual model)

FindRcAccounts = SchemasFindRcAccounts[AssetVestsHF26]

# get API responses (have no unnecessary nested  properties, just the model itself)

Config = GetConfig
DynamicGlobalProperties = GetDynamicGlobalProperties
FeedHistory = GetFeedHistory
HardforkProperties = GetHardforkProperties
Version = GetVersion
WitnessSchedule = GetWitnessSchedule

# extensions

RecurrentTransferPairIdExtension = RecurrentTransferPairId
RecurrentTransferPairIdRepresentation = HF26Representation[RecurrentTransferPairIdExtension]

# basic fields

ChainId = Sha256

# compound models

Account = AccountItemFundament[AssetHiveHF26, AssetHbdHF26, AssetVestsHF26]
ChangeRecoveryAccountRequest = ListChangeRecoveryAccountRequestsFundament
DeclineVotingRightsRequest = ListDeclineVotingRightsRequestsFundament
HbdExchangeRate = SchemasHbdExchangeRate[AssetHiveHF26, AssetHbdHF26]
PriceFeed = Price[AssetHiveHF26, AssetHbdHF26, AssetVestsHF26]
Proposal = SchemasProposal[AssetHbdHF26]
RcAccount = SchemasRcAccount[AssetVestsHF26]
RecurrentTransfer = FindRecurrentTransfersFundament[AssetHiveHF26, AssetHbdHF26]
SavingsWithdrawal = SavingsWithdrawalsFundament[AssetHiveHF26, AssetHbdHF26]
TransactionStatus = FindTransaction
VestingDelegation = VestingDelegationsFundament
VestingDelegationExpiration = VestingDelegationExpirationsFundament[AssetVestsHF26]
WithdrawRoute = WithdrawVestingRoutesFundament
Witness = WitnessesFundament[AssetHiveHF26, AssetHbdHF26]

# policies

ExtraFieldsPolicy = ExtraFields
MissingFieldsInGetConfigPolicy = MissingFieldsInGetConfig

# other

RepresentationBase = HF26Representation

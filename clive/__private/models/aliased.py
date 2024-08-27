from __future__ import annotations

from schemas._operation_objects import Hf26ApiOperationObject, Hf26ApiVirtualOperationObject
from schemas.apis.database_api import (
    FindAccounts,
    FindProposals,
    FindRecurrentTransfers,
    FindVestingDelegationExpirations,
    FindWitnesses,
    GetConfig,
    GetDynamicGlobalProperties,
    GetFeedHistory,
    GetHardforkProperties,
    GetVersion,
    GetWitnessSchedule,
    ListProposals,
    ListProposalVotes,
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
from schemas.apis.rc_api.fundaments_of_responses import RcAccount as SchemasRcAccount
from schemas.apis.transaction_status_api import FindTransaction
from schemas.fields.assets import AssetHbdHF26, AssetHiveHF26, AssetVestsHF26
from schemas.fields.assets._base import AssetBase
from schemas.fields.basic import AccountName
from schemas.fields.compound import HbdExchangeRate as SchemasHbdExchangeRate
from schemas.fields.compound import Price
from schemas.fields.compound import Proposal as SchemasProposal
from schemas.fields.hex import Sha256, Signature, TransactionId
from schemas.fields.hive_int import HiveInt
from schemas.fields.serializable import Serializable
from schemas.operation import Operation
from schemas.operations import AnyOperation, CustomJsonOperation, TransferOperation
from schemas.operations.extensions.recurrent_transfer_extensions import RecurrentTransferPairId
from schemas.operations.recurrent_transfer_operation import RecurrentTransferOperation
from schemas.operations.representation_types import Hf26OperationRepresentationType
from schemas.operations.representations.hf26_representation import HF26Representation
from schemas.operations.virtual import AnyVirtualOperation
from schemas.operations.virtual.representation_types import Hf26VirtualOperationRepresentationType
from schemas.virtual_operation import VirtualOperation

__all__ = [
    # operation BASIC aliases
    "ApiOperationObject",
    "OperationBase",
    "OperationRepresentationBase",
    "OperationRepresentationUnion",
    "OperationUnion",
    # virtual operation BASIC aliases
    "ApiVirtualOperationObject",
    "VirtualOperationBase",
    "VirtualOperationRepresentationUnion",
    "VirtualOperationUnion",
    # list API responses (have nested list property which stores actual model)
    "ListProposals",
    "ListProposalVotes",
    "ListWitnesses",
    "ListWitnessVotes",
    # find API response aliases (have nested list property which stores actual model)
    "FindAccounts",
    "FindProposals",
    "FindRcAccounts",
    "FindRecurrentTransfers",
    "FindVestingDelegationExpirations",
    "FindWitnesses",
    # get API responses (have single model as a response, we name them with model itself)
    "Config",
    "DynamicGlobalProperties",
    "FeedHistory",
    "HardforkProperties",
    "Version",
    "WitnessSchedule",
    # operations
    "CustomJsonOperation",
    "RecurrentTransferOperation",
    "TransferOperation",
    # extensions
    "RecurrentTransferPairIdExtension",
    "RecurrentTransferPairIdRepresentation",
    # basic fields
    "AccountName",
    "ChainId",
    "HiveInt",
    "Signature",
    "TransactionId",
    # compound models
    "Account",
    "ChangeRecoveryAccountRequest",
    "DeclineVotingRightsRequest",
    "HbdExchangeRate",
    "OwnerHistory",
    "PriceFeed",
    "Proposal",
    "RcAccount",
    "RecurrentTransfer",
    "SavingsWithdrawal",
    "TransactionStatus",
    "VestingDelegation",
    "VestingDelegationExpiration",
    "WithdrawRoute",
    "Witness",
    # other
    "AssetBase",
    "Serializable",
]

# operation BASIC aliases

ApiOperationObject = Hf26ApiOperationObject
OperationBase = Operation
OperationRepresentationBase = HF26Representation[OperationBase]
OperationRepresentationUnion = Hf26OperationRepresentationType
OperationUnion = AnyOperation

# virtual operation BASIC aliases

ApiVirtualOperationObject = Hf26ApiVirtualOperationObject
VirtualOperationBase = VirtualOperation
VirtualOperationRepresentationUnion = Hf26VirtualOperationRepresentationType
VirtualOperationUnion = AnyVirtualOperation

# find API response aliases (have nested list property which stores actual model)

FindRcAccounts = SchemasFindRcAccounts[AssetVestsHF26]

# get API responses (have single model as a response)

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
OwnerHistory = OwnerHistoriesFundament
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

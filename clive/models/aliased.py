from __future__ import annotations

from schemas._operation_objects import Hf26ApiOperationObject, Hf26ApiVirtualOperationObject
from schemas.apis.database_api import FindAccounts as SchemasFindAccounts
from schemas.apis.database_api import FindProposals as SchemasFindProposals
from schemas.apis.database_api import FindRecurrentTransfers as SchemasFindRecurrentTransfers
from schemas.apis.database_api import FindVestingDelegationExpirations as SchemasFindVestingDelegationExpirations
from schemas.apis.database_api import FindWitnesses as SchemasFindWitnesses
from schemas.apis.database_api import (
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
from schemas.apis.transaction_status_api import FindTransaction as SchemasFindTransaction
from schemas.fields.assets import AssetHbdHF26, AssetHiveHF26, AssetVestsHF26
from schemas.fields.assets._base import AssetBase as SchemasAssetBase
from schemas.fields.basic import AccountName as SchemasAccountName
from schemas.fields.compound import HbdExchangeRate as SchemasHbdExchangeRate
from schemas.fields.compound import Price, Proposal
from schemas.fields.hex import Sha256
from schemas.fields.hex import Signature as SchemasSignature
from schemas.fields.hive_int import HiveInt as SchemasHiveInt
from schemas.operation import Operation as SchemasBaseOperationType
from schemas.operations import AnyOperation
from schemas.operations.extensions.recurrent_transfer_extensions import RecurrentTransferPairId
from schemas.operations.recurrent_transfer_operation import (
    RecurrentTransferOperation as SchemasRecurrentTransferOperation,
)
from schemas.operations.representation_types import Hf26OperationRepresentationType
from schemas.operations.representations.hf26_representation import HF26Representation
from schemas.operations.virtual import AnyVirtualOperation
from schemas.operations.virtual.representation_types import Hf26VirtualOperationRepresentationType
from schemas.virtual_operation import VirtualOperation as SchemasBaseVirtualOperationType

AccountName = SchemasAccountName
ApiOperationObject = Hf26ApiOperationObject
ApiVirtualOperationObject = Hf26ApiVirtualOperationObject
AssetBase = SchemasAssetBase
ChainIdSchema = Sha256
ChangeRecoveryAccountRequest = ListChangeRecoveryAccountRequestsFundament
Config = GetConfig
CurrentPriceFeed = Price[AssetHiveHF26, AssetHbdHF26, AssetVestsHF26]
DeclineVotingRightsRequest = ListDeclineVotingRightsRequestsFundament
DynamicGlobalProperties = GetDynamicGlobalProperties
FeedHistory = GetFeedHistory
FindAccounts = SchemasFindAccounts
FindProposals = SchemasFindProposals
FindRecurrentTransfers = SchemasFindRecurrentTransfers
FindRcAccounts = SchemasFindRcAccounts[AssetVestsHF26]
FindVestingDelegationExpirations = SchemasFindVestingDelegationExpirations
FindWitnesses = SchemasFindWitnesses
HardforkProperties = GetHardforkProperties
HbdExchangeRate = SchemasHbdExchangeRate[AssetHiveHF26, AssetHbdHF26]
HiveInt = SchemasHiveInt
Operation = AnyOperation
OperationBaseClass = SchemasBaseOperationType
OperationRepresentationType = Hf26OperationRepresentationType
HF26OperationRepresentation = HF26Representation
OwnerHistory = OwnerHistoriesFundament
ProposalSchema = Proposal[AssetHbdHF26]
ProposalVotes = ListProposalVotes
ProposalsList = ListProposals
RcAccount = SchemasRcAccount[AssetVestsHF26]
RecurrentTransferOperation = SchemasRecurrentTransferOperation
RecurrentTransferPairIdOperationExtension = RecurrentTransferPairId
SavingsWithdrawals = SavingsWithdrawalsFundament[AssetHiveHF26, AssetHbdHF26]
SchemasAccount = AccountItemFundament[AssetHiveHF26, AssetHbdHF26, AssetVestsHF26]
Signature = SchemasSignature
TransactionStatus = SchemasFindTransaction
RecurrentTransfer = FindRecurrentTransfersFundament[AssetHiveHF26, AssetHbdHF26]
Version = GetVersion
VestingDelegation = VestingDelegationsFundament
VestingDelegationExpiration = VestingDelegationExpirationsFundament[AssetVestsHF26]
VirtualOperation = AnyVirtualOperation
VirtualOperationBaseClass = SchemasBaseVirtualOperationType
VirtualOperationRepresentationType = Hf26VirtualOperationRepresentationType
WithdrawRouteSchema = WithdrawVestingRoutesFundament
Witness = WitnessesFundament[AssetHiveHF26, AssetHbdHF26]
WitnessSchedule = GetWitnessSchedule
WitnessVotes = ListWitnessVotes
WitnessesList = ListWitnesses

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
)
from schemas.apis.database_api import (
    ListProposals as SchemasListProposals,
)
from schemas.apis.database_api import (
    ListProposalVotes as SchemasListProposalVotes,
)
from schemas.apis.database_api import (
    ListWitnesses as SchemasListWitnesses,
)
from schemas.apis.database_api import (
    ListWitnessVotes as SchemasListWitnessVotes,
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
from schemas.fields.compound import Price
from schemas.fields.compound import Proposal as SchemasProposal
from schemas.fields.hex import Sha256
from schemas.fields.hex import Signature as SchemasSignature
from schemas.fields.hex import TransactionId as SchemasTransactionId
from schemas.fields.hive_int import HiveInt as SchemasHiveInt
from schemas.fields.serializable import Serializable as SchemasSerializable
from schemas.operation import Operation
from schemas.operations import AnyOperation
from schemas.operations import CustomJsonOperation as SchemasCustomJsonOperation
from schemas.operations import TransferOperation as SchemasTransferOperation
from schemas.operations.extensions.recurrent_transfer_extensions import RecurrentTransferPairId
from schemas.operations.recurrent_transfer_operation import (
    RecurrentTransferOperation as SchemasRecurrentTransferOperation,
)
from schemas.operations.representation_types import Hf26OperationRepresentationType
from schemas.operations.representations.hf26_representation import HF26Representation
from schemas.operations.virtual import AnyVirtualOperation
from schemas.operations.virtual.representation_types import Hf26VirtualOperationRepresentationType
from schemas.virtual_operation import VirtualOperation

Account = AccountItemFundament[AssetHiveHF26, AssetHbdHF26, AssetVestsHF26]
AccountName = SchemasAccountName
ApiOperationObject = Hf26ApiOperationObject
ApiVirtualOperationObject = Hf26ApiVirtualOperationObject
AssetBase = SchemasAssetBase
ChainId = Sha256
ChangeRecoveryAccountRequest = ListChangeRecoveryAccountRequestsFundament
Config = GetConfig
CustomJsonOperation = SchemasCustomJsonOperation
DeclineVotingRightsRequest = ListDeclineVotingRightsRequestsFundament
DynamicGlobalProperties = GetDynamicGlobalProperties
FeedHistory = GetFeedHistory
FindAccounts = SchemasFindAccounts
FindProposals = SchemasFindProposals
FindRcAccounts = SchemasFindRcAccounts[AssetVestsHF26]
FindRecurrentTransfers = SchemasFindRecurrentTransfers
FindVestingDelegationExpirations = SchemasFindVestingDelegationExpirations
FindWitnesses = SchemasFindWitnesses
HardforkProperties = GetHardforkProperties
HbdExchangeRate = SchemasHbdExchangeRate[AssetHiveHF26, AssetHbdHF26]
HiveInt = SchemasHiveInt
ListProposals = SchemasListProposals
ListProposalVotes = SchemasListProposalVotes
ListWitnesses = SchemasListWitnesses
ListWitnessVotes = SchemasListWitnessVotes
OperationBase = Operation
OperationRepresentationBase = HF26Representation[OperationBase]
OperationRepresentationUnion = Hf26OperationRepresentationType
OperationUnion = AnyOperation
OwnerHistory = OwnerHistoriesFundament
PriceFeed = Price[AssetHiveHF26, AssetHbdHF26, AssetVestsHF26]
Proposal = SchemasProposal[AssetHbdHF26]
RcAccount = SchemasRcAccount[AssetVestsHF26]
RecurrentTransfer = FindRecurrentTransfersFundament[AssetHiveHF26, AssetHbdHF26]
RecurrentTransferOperation = SchemasRecurrentTransferOperation
RecurrentTransferPairIdOperationExtension = RecurrentTransferPairId
RecurrentTransferPairIdRepresentation = HF26Representation[RecurrentTransferPairIdOperationExtension]
SavingsWithdrawal = SavingsWithdrawalsFundament[AssetHiveHF26, AssetHbdHF26]
Serializable = SchemasSerializable
Signature = SchemasSignature
TransactionId = SchemasTransactionId
TransactionStatus = SchemasFindTransaction
TransferOperation = SchemasTransferOperation
Version = GetVersion
VestingDelegation = VestingDelegationsFundament
VestingDelegationExpiration = VestingDelegationExpirationsFundament[AssetVestsHF26]
VirtualOperationBase = VirtualOperation
VirtualOperationRepresentationUnion = Hf26VirtualOperationRepresentationType
VirtualOperationUnion = AnyVirtualOperation
WithdrawRoute = WithdrawVestingRoutesFundament
Witness = WitnessesFundament[AssetHiveHF26, AssetHbdHF26]
WitnessSchedule = GetWitnessSchedule

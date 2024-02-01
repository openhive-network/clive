from __future__ import annotations

from schemas._operation_objects import Hf26ApiOperationObject, Hf26ApiVirtualOperationObject
from schemas.apis.database_api import FindAccounts as SchemasFindAccounts
from schemas.apis.database_api import FindProposals as SchemasFindProposals
from schemas.apis.database_api import FindWitnesses as SchemasFindWitnesses
from schemas.apis.database_api import (
    GetDynamicGlobalProperties,
    ListProposals,
    ListProposalVotes,
    ListWitnesses,
    ListWitnessVotes,
)
from schemas.apis.database_api.fundaments_of_reponses import (
    AccountItemFundament,
    ListChangeRecoveryAccountRequestsFundament,
    ListDeclineVotingRightsRequestsFundament,
    OwnerHistoriesFundament,
    SavingsWithdrawalsFundament,
    WithdrawVestingRoutesFundament,
    WitnessesFundament,
)
from schemas.apis.rc_api import FindRcAccounts as SchemasFindRcAccounts
from schemas.apis.rc_api.fundaments_of_responses import RcAccount as SchemasRcAccount
from schemas.apis.reputation_api.fundaments_of_responses import GetAccountReputationsFundament
from schemas.apis.transaction_status_api import FindTransaction as SchemasFindTransaction
from schemas.fields.assets import AssetHbdHF26, AssetHiveHF26, AssetVestsHF26
from schemas.fields.assets._base import AssetBase as SchemasAssetBase
from schemas.fields.basic import AccountName as SchemasAccountName
from schemas.fields.compound import Proposal
from schemas.fields.hex import Sha256
from schemas.fields.hex import Signature as SchemasSignature
from schemas.operation import Operation as SchemasBaseOperationType
from schemas.operations import AnyOperation
from schemas.operations.representation_types import Hf26OperationRepresentationType
from schemas.operations.virtual import AnyVirtualOperation
from schemas.operations.virtual.representation_types import Hf26VirtualOperationRepresentationType
from schemas.virtual_operation import VirtualOperation as SchemasBaseVirtualOperationType

AssetBase = SchemasAssetBase
Operation = AnyOperation
VirtualOperation = AnyVirtualOperation
OperationBaseClass = SchemasBaseOperationType
VirtualOperationBaseClass = SchemasBaseVirtualOperationType
OperationRepresentationType = Hf26OperationRepresentationType
VirtualOperationRepresentationType = Hf26VirtualOperationRepresentationType
ApiOperationObject = Hf26ApiOperationObject
ApiVirtualOperationObject = Hf26ApiVirtualOperationObject
Signature = SchemasSignature
AccountName = SchemasAccountName

ProposalSchema = Proposal[AssetHbdHF26]
ProposalsList = ListProposals
ProposalVotes = ListProposalVotes
FindWitnesses = SchemasFindWitnesses
WitnessVotes = ListWitnessVotes
WitnessesList = ListWitnesses
Reputation = GetAccountReputationsFundament
OwnerHistory = OwnerHistoriesFundament
FindRcAccounts = SchemasFindRcAccounts[AssetVestsHF26]
SavingsWithdrawals = SavingsWithdrawalsFundament[AssetHiveHF26, AssetHbdHF26]
Witness = WitnessesFundament[AssetHiveHF26, AssetHbdHF26]
SchemasAccount = AccountItemFundament[AssetHiveHF26, AssetHbdHF26, AssetVestsHF26]
RcAccount = SchemasRcAccount[AssetVestsHF26]
DynamicGlobalProperties = GetDynamicGlobalProperties
TransactionStatus = SchemasFindTransaction
FindProposals = SchemasFindProposals
FindAccounts = SchemasFindAccounts
WithdrawRouteSchema = WithdrawVestingRoutesFundament

ChangeRecoveryAccountRequest = ListChangeRecoveryAccountRequestsFundament
DeclineVotingRightsRequest = ListDeclineVotingRightsRequestsFundament

ChainIdSchema = Sha256

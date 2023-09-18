from __future__ import annotations

from clive.models.asset import Asset
from schemas._operation_objects import Hf26ApiOperationObject, Hf26ApiVirtualOperationObject
from schemas.apis.database_api.fundaments_of_reponses import SavingsWithdrawalsFundament
from schemas.fields.assets._base import AssetBase as SchemasAssetBase
from schemas.fields.basic import AccountName as SchemasAccountName
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
SavingsWithdrawals = SavingsWithdrawalsFundament[Asset.Hive, Asset.Hbd]

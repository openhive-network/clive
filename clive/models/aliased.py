from __future__ import annotations

from schemas.__private.hive_fields_basic_schemas import AccountName as SchemasAccountName
from schemas.__private.hive_fields_basic_schemas import AssetBase as SchemasAssetBase
from schemas.__private.hive_fields_custom_schemas import Signature as SchemasSignature
from schemas.__private.operation import Operation as SchemasBaseOperationType
from schemas.__private.operation_objects import Hf26ApiOperationObject, Hf26ApiVirtualOperationObject
from schemas.__private.virtual_operation import VirtualOperation as SchemasBaseVirtualOperationType
from schemas.operations import (
    AnyOperation,
    Hf26OperationRepresentationType,
)
from schemas.virtual_operations import (
    AnyVirtualOperation,
    Hf26VirtualOperationRepresentationType,
)

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

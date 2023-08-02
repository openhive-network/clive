from __future__ import annotations

from typing import Any

from schemas.__private.hive_fields_basic_schemas import AssetBase as SchemasAssetBase
from schemas.__private.hive_fields_custom_schemas import Signature as SchemasSignature
from schemas.__private.operation_objects import Hf26ApiOperationObject, Hf26ApiVirtualOperationObject
from schemas.__private.operations import (
    Hf26OperationRepresentation as __Hf26OperationRepresentationBase,  # such name is used to avoid showing in suggested imports
)
from schemas.__private.operations import (
    Hf26OperationRepresentationType,
    Hf26OperationType,
    Hf26VirtualOperationRepresentationType,
    Hf26VirtualOperationType,
    get_hf26_representation,
)
from schemas.__private.operations import (
    LegacyOperationRepresentation as __LegacyOperationRepresentationBase,  # such name is used to avoid showing in suggested imports
)
from schemas.__private.preconfigured_base_model import Operation as SchemasBaseOperationType
from schemas.__private.preconfigured_base_model import VirtualOperation as SchemasBaseVirtualOperationType

AssetBase = SchemasAssetBase
Operation = Hf26OperationType
VirtualOperation = Hf26VirtualOperationType
OperationBaseClass = SchemasBaseOperationType
VirtualOperationBaseClass = SchemasBaseVirtualOperationType
OperationRepresentationType = Hf26OperationRepresentationType
VirtualOperationRepresentationType = Hf26VirtualOperationRepresentationType
ApiOperationObject = Hf26ApiOperationObject
ApiVirtualOperationObject = Hf26ApiVirtualOperationObject
Signature = SchemasSignature


def convert_to_representation(
    operation: Operation | VirtualOperation | Any,
) -> OperationRepresentationType | VirtualOperationRepresentationType:
    assert isinstance(
        operation,
        OperationBaseClass | __LegacyOperationRepresentationBase | __Hf26OperationRepresentationBase,
    ), "not supported type"

    if isinstance(operation, __LegacyOperationRepresentationBase):
        operation = operation.value
    if isinstance(operation, __Hf26OperationRepresentationBase):
        return operation
    return get_hf26_representation(operation.get_name())(type=operation.get_name(), value=operation)

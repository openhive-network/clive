from __future__ import annotations

from typing import TYPE_CHECKING

from clive.models.aliased import OperationBaseClass
from schemas.__private.operations import (
    Hf26OperationRepresentation as __Hf26OperationRepresentationBase,  # such name is used to avoid showing in suggested imports
)
from schemas.__private.operations import (
    LegacyOperationRepresentation as __LegacyOperationRepresentationBase,  # such name is used to avoid showing in suggested imports
)
from schemas.__private.operations import get_hf26_representation

if TYPE_CHECKING:
    from typing import Any

    from clive.models.aliased import (
        Operation,
        OperationRepresentationType,
        VirtualOperation,
        VirtualOperationRepresentationType,
    )


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
    return get_hf26_representation(operation.get_name())(type=operation.get_name_with_suffix(), value=operation)

from __future__ import annotations

from typing import Generic, TypeVar

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import ID_PLACEHOLDER
from schemas.__private.hive_fields_basic_schemas import Int64t, Uint16t, Uint32t

OrderIdT = Uint32t
EscrowIdT = Uint32t
BlockIdT = Uint32t
RequestIdT = Uint32t

IdT = Uint16t

ProposalIdT = Int64t

HiveIdT = TypeVar("HiveIdT", OrderIdT, EscrowIdT, BlockIdT, IdT, ProposalIdT)


class IdInput(CustomInput, Generic[HiveIdT]):
    """To use this input specify by generic one of above type of id."""

    def __init__(self, label: str = "id", value: int | None = None, placeholder: str = ID_PLACEHOLDER) -> None:
        super().__init__(label=label, value=str(value), placeholder=placeholder)

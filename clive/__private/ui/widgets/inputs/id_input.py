from __future__ import annotations

from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.placeholders_constants import ID_PLACEHOLDER


class IdInput(IntegerInput):
    """To use this input specify by generic one of above type of id."""

    def __init__(self, label: str = "id", value: int | None = None, placeholder: str = ID_PLACEHOLDER) -> None:
        super().__init__(label=label, value=value, placeholder=placeholder)

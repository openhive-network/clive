from __future__ import annotations

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import INTEGER_PLACEHOLDER


class IntegerInput(CustomInput[int]):
    def __init__(self, label: str, value: int | None = None, placeholder: str = INTEGER_PLACEHOLDER):
        super().__init__(label=label, value=value, placeholder=placeholder)

    @property
    def value(self) -> int:
        return int(self._input.value)

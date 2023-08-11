from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import INTEGER_PLACEHOLDER

if TYPE_CHECKING:
    from textual.widget import Widget


class IntegerInput(CustomInput[int]):
    def __init__(self, to_mount: Widget, label: str, value: int | None = None, placeholder: str = INTEGER_PLACEHOLDER):
        super().__init__(to_mount=to_mount, label=label, value=value, placeholder=placeholder)

    @property
    def value(self) -> int:
        return int(self._input.value)

from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import INTEGER_PLACEHOLDER

if TYPE_CHECKING:
    from rich.highlighter import Highlighter


class IntegerInput(CustomInput[int]):
    def __init__(
        self,
        label: str,
        value: int | None = None,
        placeholder: str = INTEGER_PLACEHOLDER,
        highlighter: Highlighter | None = None,
    ):
        super().__init__(label=label, value=value, placeholder=placeholder, highlighter=highlighter)

    @property
    def value(self) -> int:
        return int(self._input.value)

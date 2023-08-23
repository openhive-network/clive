from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import NUMERIC_PLACEHOLDER

if TYPE_CHECKING:
    from rich.console import RenderableType


class NumericInput(CustomInput[float | None]):
    def __init__(
        self,
        label: str = "amount",
        value: float | None = None,
        *,
        placeholder: str = NUMERIC_PLACEHOLDER,
        tooltip: RenderableType | None = None,
        disabled: bool = False,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            label=label,
            value=value,
            placeholder=placeholder,
            tooltip=tooltip,
            disabled=disabled,
            id_=id_,
            classes=classes,
        )

    @property
    def value(self) -> float | None:
        try:
            return float(self._input.value)
        except ValueError:
            self.notify("The specified string could not be converted to a numeric value", severity="error")
            return None

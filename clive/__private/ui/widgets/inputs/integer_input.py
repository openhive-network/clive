from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import INTEGER_PLACEHOLDER

if TYPE_CHECKING:
    from rich.console import RenderableType

    from clive.__private.ui.widgets.clive_highlighter import CliveHighlighter


class IntegerInput(CustomInput[int | None]):
    def __init__(
        self,
        label: str = "amount",
        value: int | None = None,
        *,
        placeholder: str = INTEGER_PLACEHOLDER,
        tooltip: RenderableType | None = None,
        disabled: bool = False,
        highlighter: CliveHighlighter | None = None,
        id_: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(
            label=label,
            value=value,
            placeholder=placeholder,
            tooltip=tooltip,
            disabled=disabled,
            highlighter=highlighter,
            id_=id_,
            classes=classes,
        )

    @property
    def value(self) -> int | None:
        try:
            return int(self._input.value)
        except ValueError:
            self.notify("The specified string could no be converted to a integer value", severity="error")
            return None

from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.clive_highlighter import CliveHighlighter
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import WITNESS_PLACEHOLDER

if TYPE_CHECKING:
    from typing import Final

    from rich.console import RenderableType

MAX_LENGTH_OF_PATTERN: Final[int] = 16


class WitnessPatternHighlighter(CliveHighlighter):
    def is_valid_value(self, value: str) -> bool:
        if len(value) > MAX_LENGTH_OF_PATTERN:
            return False
        return True


class WitnessPatternInput(TextInput):
    def __init__(
        self,
        label: str = "witness",
        value: str | None = None,
        *,
        placeholder: str = WITNESS_PLACEHOLDER,
        tooltip: RenderableType | None = None,
        disabled: bool = False,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            label=label,
            value=value,
            placeholder=placeholder,
            highlighter=WitnessPatternHighlighter(),
            tooltip=tooltip,
            disabled=disabled,
            id_=id_,
            classes=classes,
        )

    @property
    def value(self) -> str | None:  # type: ignore[override]
        value = self._input.value

        if len(value) > MAX_LENGTH_OF_PATTERN:
            self.notify("Must be shorter than 16!", severity="error")
            return None
        return value

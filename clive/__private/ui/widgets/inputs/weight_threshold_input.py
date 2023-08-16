from __future__ import annotations

from typing import TYPE_CHECKING, Final

from rich.highlighter import Highlighter

from clive.__private.ui.widgets.inputs.integer_input import IntegerInput

if TYPE_CHECKING:
    from rich.text import Text


class WeightThresholdHighlighter(Highlighter):
    MAX_VALUE_OF_WEIGHT: Final[int] = 4294967295
    MIN_VALUE_OF_WEIGHT: Final[int] = 0

    @classmethod
    def is_valid_weight(cls, weight: str) -> bool:
        return cls.MIN_VALUE_OF_WEIGHT <= int(weight) <= cls.MAX_VALUE_OF_WEIGHT

    def highlight(self, text: Text) -> None:
        if self.is_valid_weight(str(text)):
            text.stylize("green")
        else:
            text.stylize("red")


class WeightThresholdInput(IntegerInput):
    def __init__(self, label: str = "weight threshold", value: int | None = None) -> None:
        super().__init__(label=label, value=value, highlighter=WeightThresholdHighlighter())

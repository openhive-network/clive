from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.integer_input import IntegerInput

if TYPE_CHECKING:
    from textual.widget import Widget


class WeightThresholdInput(IntegerInput):
    def __init__(self, to_mount: Widget, label: str = "weight threshold", value: int | None = None) -> None:
        super().__init__(to_mount=to_mount, label=label, value=value)

from __future__ import annotations

from clive.__private.ui.widgets.inputs.integer_input import IntegerInput


class WeightThresholdInput(IntegerInput):
    def __init__(self, label: str = "weight threshold", value: int | None = None) -> None:
        super().__init__(label=label, value=value)

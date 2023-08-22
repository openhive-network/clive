from __future__ import annotations

from clive.__private.ui.widgets.inputs.numeric_input import NumericInput


class FeeInput(NumericInput):
    def __init__(self, label: str = "fee", value: float | None = None) -> None:
        super().__init__(label=label, value=value)

from __future__ import annotations

from clive.__private.ui.widgets.inputs.amount_input import AmountInput


class FeeInput(AmountInput):
    def __init__(self, label: str = "fee", value: float | None = None) -> None:
        super().__init__(label=label, value=value)

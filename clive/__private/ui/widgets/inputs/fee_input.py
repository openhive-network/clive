from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.amount_input import AmountInput

if TYPE_CHECKING:
    from textual.widget import Widget


class FeeInput(AmountInput):
    def __init__(self, to_mount: Widget, label: str = "fee", value: float | None = None) -> None:
        super().__init__(to_mount=to_mount, label=label, value=value)

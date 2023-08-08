from __future__ import annotations

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import ASSET_AMOUNT_PLACEHOLDER


class AmountInput(CustomInput):
    def __init__(
        self, label: str = "amount", value: float | int | None = None, placeholder: str = ASSET_AMOUNT_PLACEHOLDER
    ) -> None:
        super().__init__(label=label, value=str(value), placeholder=placeholder)

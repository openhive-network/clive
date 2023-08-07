from __future__ import annotations

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import ASSET_AMOUNT_PLACEHOLDER


class FeeInput(CustomInput):
    def __init__(
        self, label: str = "fee", value: str | None = None, placeholder: str = ASSET_AMOUNT_PLACEHOLDER
    ) -> None:
        super().__init__(label=label, value=value, placeholder=placeholder)

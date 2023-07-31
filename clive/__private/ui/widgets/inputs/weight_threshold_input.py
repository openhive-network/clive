from __future__ import annotations

from clive.__private.ui.widgets.inputs.base_input import BaseInput
from clive.__private.ui.widgets.placeholders_constants import WEIGHT_THRESHOLD_PLACEHOLDER


class WeightThresholdInput(BaseInput):
    def __init__(
        self, label: str = "", value: str | None = None, placeholder: str = WEIGHT_THRESHOLD_PLACEHOLDER
    ) -> None:
        super().__init__(label=label, default_value=value, placeholder=placeholder)

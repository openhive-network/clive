from __future__ import annotations

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import DATE_PLACEHOLDER


class DateInput(CustomInput):
    def __init__(self, label: str = "date", value: str | None = None, placeholder: str = DATE_PLACEHOLDER) -> None:
        super().__init__(label=label, value=value, placeholder=placeholder)

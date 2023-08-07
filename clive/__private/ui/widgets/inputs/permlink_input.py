from __future__ import annotations

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import PERMLINK_PLACEHOLDER


class PermlinkInput(CustomInput):
    def __init__(
        self, label: str = "permlink", value: str | None = None, placeholder: str = PERMLINK_PLACEHOLDER
    ) -> None:
        super().__init__(label=label, value=value, placeholder=placeholder)

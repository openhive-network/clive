from __future__ import annotations

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import KEY_AUTHS_PLACEHOLDER


class KeyAuthsInput(CustomInput):
    def __init__(self, label: str = "", value: str | None = None, placeholder: str = KEY_AUTHS_PLACEHOLDER) -> None:
        super().__init__(label=label, value=value, placeholder=placeholder)

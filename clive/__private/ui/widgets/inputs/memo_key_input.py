from __future__ import annotations

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import KEY_PLACEHOLDER


class MemoKeyInput(CustomInput):
    def __init__(self, label: str = "memo key", placeholder: str = KEY_PLACEHOLDER, value: str | None = None):
        super().__init__(label=label, placeholder=placeholder, value=value)

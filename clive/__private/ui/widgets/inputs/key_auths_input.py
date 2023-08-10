from __future__ import annotations

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import KEY_AUTHS_PLACEHOLDER


class KeyAuthsInput(TextInput):
    def __init__(
        self, label: str = "key auths", value: str | None = None, placeholder: str = KEY_AUTHS_PLACEHOLDER
    ) -> None:
        super().__init__(label=label, value=value, placeholder=placeholder)

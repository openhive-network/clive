from __future__ import annotations

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_AUTHS_PLACEHOLDER


class AccountAuthsInput(TextInput):
    def __init__(
        self, label: str = "account auths", value: str | None = None, placeholder: str = ACCOUNT_AUTHS_PLACEHOLDER
    ) -> None:
        super().__init__(label=label, value=value, placeholder=placeholder)

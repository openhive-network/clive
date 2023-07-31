from __future__ import annotations

from clive.__private.ui.widgets.inputs.base_input import BaseInput
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_AUTHS_PLACEHOLDER


class AccountAuthsInput(BaseInput):
    def __init__(self, label: str = "", value: str | None = None, placeholder: str = ACCOUNT_AUTHS_PLACEHOLDER) -> None:
        super().__init__(label=label, default_value=value, placeholder=placeholder)

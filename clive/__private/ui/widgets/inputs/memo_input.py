from __future__ import annotations

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import MEMO_PLACEHOLDER


class MemoInput(CustomInput):
    def __init__(self, label: str = "memo", placeholder: str = MEMO_PLACEHOLDER, value: str | None = None):
        super().__init__(label=label, placeholder=placeholder, value=value)

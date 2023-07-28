from __future__ import annotations

from clive.__private.ui.widgets.inputs.base_input import BaseInput
from clive.__private.ui.widgets.placeholders_constants import MEMO_PLACEHOLDER


class MemoInput(BaseInput):
    def __init__(self, label: str = "", placeholder: str = MEMO_PLACEHOLDER, value: str | None = None):
        super().__init__(label=label, placeholder=placeholder, default_value=value)

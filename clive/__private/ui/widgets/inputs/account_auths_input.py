from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_AUTHS_PLACEHOLDER

if TYPE_CHECKING:
    from textual.widget import Widget


class AccountAuthsInput(TextInput):
    def __init__(
        self,
        to_mount: Widget,
        label: str = "account auths",
        value: str | None = None,
        placeholder: str = ACCOUNT_AUTHS_PLACEHOLDER,
    ) -> None:
        super().__init__(to_mount=to_mount, label=label, value=value, placeholder=placeholder)

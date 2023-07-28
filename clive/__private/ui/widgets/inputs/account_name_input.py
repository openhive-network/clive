from __future__ import annotations

from clive.__private.ui.set_account.set_account import AccountNameHighlighter
from clive.__private.ui.widgets.inputs.base_input import BaseInput
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_NAME_PLACEHOLDER


class AccountNameInput(BaseInput):
    def __init__(
        self,
        label: str = "",
        placeholder: str = ACCOUNT_NAME_PLACEHOLDER,
        default_value: str | None = None,
        id_: str | None = None,
    ) -> None:
        super().__init__(
            label=label,
            placeholder=placeholder,
            default_value=default_value,
            highlighter=AccountNameHighlighter(),
            id_=id_,
        )

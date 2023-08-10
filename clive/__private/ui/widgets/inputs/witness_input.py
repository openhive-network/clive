from __future__ import annotations

from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.placeholders_constants import WITNESS_PLACEHOLDER


class WitnessInput(AccountNameInput):
    def __init__(
        self,
        label: str = "witness",
        value: str | None = None,
        placeholder: str = WITNESS_PLACEHOLDER,
        id_: str | None = None,
    ) -> None:
        super().__init__(label=label, value=value, placeholder=placeholder, id_=id_)

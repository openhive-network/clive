from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.placeholders_constants import WITNESS_PLACEHOLDER

if TYPE_CHECKING:
    from rich.console import RenderableType


class WitnessInput(AccountNameInput):
    def __init__(
        self,
        label: str = "witness",
        value: str | None = None,
        *,
        placeholder: str = WITNESS_PLACEHOLDER,
        tooltip: RenderableType | None = None,
        disabled: bool = False,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            label=label,
            value=value,
            placeholder=placeholder,
            tooltip=tooltip,
            disabled=disabled,
            id_=id_,
            classes=classes,
        )

from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import KEY_AUTHS_PLACEHOLDER

if TYPE_CHECKING:
    from rich.console import RenderableType


class KeyAuthsInput(TextInput):
    def __init__(
        self,
        label: str = "key auths",
        value: str | None = None,
        *,
        placeholder: str = KEY_AUTHS_PLACEHOLDER,
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

from __future__ import annotations

from clive.__private.ui.widgets.inputs.custom_input import CustomInput


class TextInput(CustomInput):
    def __init__(self, label: str, value: str | None = None, placeholder: str = "") -> None:
        super().__init__(label=label, value=value, placeholder=placeholder)

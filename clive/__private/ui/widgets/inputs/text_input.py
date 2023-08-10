from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.custom_input import CustomInput

if TYPE_CHECKING:
    from rich.highlighter import Highlighter


class TextInput(CustomInput[str]):
    def __init__(
        self,
        label: str,
        value: str | None = None,
        placeholder: str = "",
        id_: str | None = None,
        highlighter: Highlighter | None = None,
        password: bool = False,
    ) -> None:
        super().__init__(
            label=label, value=value, placeholder=placeholder, id_=id_, highlighter=highlighter, password=password
        )

    @property
    def value(self) -> str:
        return self._input.value

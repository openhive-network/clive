from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.custom_input import CustomInput

if TYPE_CHECKING:
    from rich.console import RenderableType
    from rich.highlighter import Highlighter


class TextInput(CustomInput[str]):
    def __init__(
        self,
        label: str,
        value: str | None = None,
        *,
        placeholder: str = "",
        tooltip: RenderableType | None = None,
        disabled: bool = False,
        highlighter: Highlighter | None = None,
        password: bool = False,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            label=label,
            value=value,
            placeholder=placeholder,
            tooltip=tooltip,
            disabled=disabled,
            password=password,
            highlighter=highlighter,
            id_=id_,
            classes=classes,
        )

    @property
    def value(self) -> str:
        return self._input.value

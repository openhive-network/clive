from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.base_input import BaseInput

if TYPE_CHECKING:
    from rich.highlighter import Highlighter


class CustomInput(BaseInput):
    """class for inputs that are not using often enough to have their own classes."""

    def __init__(
        self,
        label: str = "",
        placeholder: str = "",
        highlighter: Highlighter | None = None,
        default_value: str | None = None,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            label=label,
            placeholder=placeholder,
            highlighter=highlighter,
            default_value=default_value,
            id_=id_,
            classes=classes,
        )

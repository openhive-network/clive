from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Input

from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.input_label import InputLabel

if TYPE_CHECKING:
    from rich.highlighter import Highlighter
    from textual.app import ComposeResult


class BaseInput(CliveWidget):
    DEFAULT_CSS = """
        BaseInput Input {
            width: 80%;
            }
    """

    def __init__(
        self,
        label: str = "",
        placeholder: str = "",
        default_value: str | None = None,
        highlighter: Highlighter | None = None,
        id_: str | None = None,
        classes: str | None = None,
    ):
        self.__label = label

        self.__input = Input(value=default_value, placeholder=placeholder, highlighter=highlighter)

        super().__init__(id=id_, classes=classes)

    def compose(self) -> ComposeResult:
        yield InputLabel(self.__label)
        yield self.__input

    @property
    def value(self) -> str:
        return self.__input.value

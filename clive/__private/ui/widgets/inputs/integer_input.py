from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Input

from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.input_label import InputLabel

if TYPE_CHECKING:
    from rich.console import RenderableType
    from rich.highlighter import Highlighter
    from textual.app import ComposeResult


class IntegerInput(CliveWidget):
    DEFAULT_CSS = """
        IntegerInput Input {
            width: 80%;
            }
    """

    def __init__(
        self,
        label: RenderableType,
        value: int | None = None,
        placeholder: str = "",
        highlighter: Highlighter | None = None,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        self.__label = label

        self.__input = Input(value=str(value), placeholder=placeholder, highlighter=highlighter)

        super().__init__(id=id_, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        yield InputLabel(self.__label)
        yield self.__input

    @property
    def value(self) -> int:
        return int(self.__input.value)

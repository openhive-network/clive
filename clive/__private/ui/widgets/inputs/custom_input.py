from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from textual.widgets import Input

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.input_label import InputLabel

if TYPE_CHECKING:
    from rich.console import RenderableType
    from rich.highlighter import Highlighter
    from textual.app import ComposeResult


ValueT = TypeVar("ValueT")


class CustomInput(CliveWidget, Generic[ValueT], AbstractClassMessagePump):
    """
    Base class for customizable input elements. Can be used both as a base class for other elements or independently.

    Examples:
    --------
    yield from instance_of_custom_input.compose()

    Note:
    ----
    When using this widget, it will not be included in the list of nodes.
    Querying this widget is not supported.
    You must use it like the way in example.
    """

    DEFAULT_CSS = """
        CustomInput Input {
            width: 80%;
            }
    """

    def __init__(
        self,
        label: RenderableType,
        value: ValueT | None = None,
        placeholder: str = "",
        highlighter: Highlighter | None = None,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        password: bool = False,
        tooltip: str | None = None,
    ):
        super().__init__(id=id_, classes=classes, disabled=disabled)

        self._input_label = InputLabel(label)

        value_processed = str(value) if value is not None else None
        self._input = Input(value_processed, placeholder=placeholder, highlighter=highlighter, password=password)
        self._input.tooltip = tooltip

    def compose(self) -> ComposeResult:
        yield self._input_label
        yield self._input

    @property
    def raw_value(self) -> str:
        return self._input.value

    @property
    @abstractmethod
    def value(self) -> ValueT:
        ...

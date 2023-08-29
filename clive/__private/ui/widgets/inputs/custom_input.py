from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from textual.widgets import Input

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.input_label import InputLabel

if TYPE_CHECKING:
    from collections.abc import Iterable

    from rich.console import RenderableType
    from rich.highlighter import Highlighter
    from textual.app import ComposeResult
    from textual.suggester import Suggester
    from textual.validation import Validator


ValueT = TypeVar("ValueT")


class CustomInput(CliveWidget, Generic[ValueT], AbstractClassMessagePump):
    """
    Base class for customizable input elements. Can be used both as a base class for other elements or independently.

    Examples:
    --------
    1. yield SomeCustomInputSubclass()
    2. yield from SomeCustomInputSubclass().compose()

    Note:
    ----
    When using this widget like showed in 2nd example, it will not be included in the list of nodes.
    That means that you can't query it or use it as a parent for other widgets for e.g. setting styles.
    """

    DEFAULT_CSS = """
        CustomInput {
            layout: horizontal;
        }
        CustomInput Input {
            width: 80%;
        }
    """

    def __init__(
        self,
        label: str,
        value: ValueT | None = None,
        *,
        placeholder: str = "",
        tooltip: RenderableType | None = None,
        disabled: bool = False,
        password: bool = False,
        highlighter: Highlighter | None = None,
        suggester: Suggester | None = None,
        validators: Validator | Iterable[Validator] | None = None,
        id_: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(disabled=disabled, id=id_, classes=classes)

        self.tooltip = tooltip

        self._label = label
        self._value_processed = str(value) if value is not None else None
        self._placeholder = placeholder
        self._password = password
        self._highlighter = highlighter
        self._suggester = suggester
        self._validators = validators

        self._input_label = InputLabel(
            label,
            id_=f"{id_}--label" if id_ else None,
        )
        self._input = self.__create_input()

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

    @property
    def input(self) -> Input:  # noqa: A003
        return self._input

    @property
    def label(self) -> InputLabel:
        return self._input_label

    def _create_input(self) -> Input:
        return Input(
            self._value_processed,
            placeholder=self._placeholder,
            disabled=self.disabled,
            password=self._password,
            highlighter=self._highlighter,
            suggester=self._suggester,
            validators=self._validators,
            id=f"{self.id}--input" if self.id else None,
        )

    def __create_input(self) -> Input:
        input_ = self._create_input()
        input_.tooltip = self._tooltip
        return input_

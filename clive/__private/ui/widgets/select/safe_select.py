from __future__ import annotations

from typing import TYPE_CHECKING, Final, Generic

from textual.widgets import Select, Static
from textual.widgets._select import SelectOption, SelectType

from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.exceptions import NoItemSelectedError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.app import ComposeResult


class EmptySelect(Static):
    DEFAULT_MESSAGE: Final[str] = "Nothing to choose from."

    DEFAULT_CSS = """
    EmptySelect {
        color: $error-lighten-1;
    }
    """

    def __init__(self, empty_message: str = DEFAULT_MESSAGE) -> None:
        super().__init__(empty_message)
        self.value = None


class SingleSelect(Static, Generic[SelectType]):
    """Dummy select widget."""

    def __init__(self, option: SelectOption[SelectType]) -> None:
        super().__init__(option[0])
        self.value = option[1]


class SafeSelect(CliveWidget, Generic[SelectType]):
    MIN_AMOUNT_OF_ITEMS: Final[int] = 2

    DEFAULT_CSS = """
    SafeSelect {
        min-height: 3;
        align: center middle;
    }
    """

    def __init__(
        self,
        options: Iterable[SelectOption[SelectType]],
        *,
        prompt: str = "Select",
        value: SelectType | None = None,
        empty_string: str = EmptySelect.DEFAULT_MESSAGE,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(id=id_, classes=classes, disabled=disabled)

        self._options = list(options)
        self._content: Select[SelectType] | SingleSelect[SelectType] | EmptySelect = EmptySelect(empty_string)
        self.__value: SelectType | None = value

        if len(self._options) >= self.MIN_AMOUNT_OF_ITEMS:
            self._content = Select(options, prompt=prompt, allow_blank=False, value=self.__value)
        elif options:
            self._content = SingleSelect(option=self._options[0])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.__value}, options={self._options}, content={self._content})"

    @property
    def value(self) -> SelectType:
        value = self._content.value
        if value is None:
            raise NoItemSelectedError(f"No item is selected yet from {self}.")
        return value

    def compose(self) -> ComposeResult:
        yield self._content

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Final

from rich.highlighter import Highlighter

from clive.__private.abstract_class import AbstractClassMessagePump

if TYPE_CHECKING:
    from rich.text import Text
    from textual.widget import Widget


class CliveHighlighter(Highlighter, AbstractClassMessagePump):
    VALID_TEXT_CSS_CLASS: Final[str] = "-valid-text"
    INVALID_TEXT_CSS_CLASS: Final[str] = "-invalid-text"

    def __init__(self) -> None:
        self.__parent: Widget | None = None

    @abstractmethod
    def is_valid_value(self, value: str) -> bool:
        """Check that the value is consistent with the schemas."""

    @property
    def parent(self) -> Widget:
        if self.__parent is None:
            raise ValueError("Parent is not set")
        return self.__parent

    @parent.setter
    def parent(self, parent: Widget) -> None:
        self.__parent = parent

    def highlight(self, text: Text) -> None:
        is_valid = self.is_valid_value(text.plain)
        self.parent.remove_class(self.VALID_TEXT_CSS_CLASS if not is_valid else self.INVALID_TEXT_CSS_CLASS)
        self.parent.add_class(self.VALID_TEXT_CSS_CLASS if is_valid else self.INVALID_TEXT_CSS_CLASS)

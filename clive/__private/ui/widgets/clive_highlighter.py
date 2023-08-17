from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from rich.highlighter import Highlighter

from clive.__private.abstract_class import AbstractClassMessagePump

if TYPE_CHECKING:
    from rich.text import Text


class CliveHighlighter(Highlighter, AbstractClassMessagePump):
    @abstractmethod
    def is_valid_value(self, value: str) -> bool:
        """Check that the value is consistent with the schemas."""

    def highlight(self, text: Text) -> None:
        if self.is_valid_value(str(text)):
            text.stylize("green")
        else:
            text.stylize("red")

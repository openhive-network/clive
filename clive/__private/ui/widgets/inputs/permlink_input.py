from __future__ import annotations

from typing import TYPE_CHECKING, Final

from rich.highlighter import Highlighter

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import PERMLINK_PLACEHOLDER

if TYPE_CHECKING:
    from rich.text import Text


class PermlinkHighlighter(Highlighter):
    MAX_PERMLINK_LENGTH: Final[int] = 256

    @classmethod
    def is_valid_permlink(cls, permlink: str) -> bool:
        return len(permlink) <= cls.MAX_PERMLINK_LENGTH

    def highlight(self, text: Text) -> None:
        if self.is_valid_permlink(str(text)):
            text.stylize("green")
        else:
            text.stylize("red")


class PermlinkInput(TextInput):
    def __init__(
        self, label: str = "permlink", value: str | None = None, placeholder: str = PERMLINK_PLACEHOLDER
    ) -> None:
        super().__init__(label=label, value=value, placeholder=placeholder, highlighter=PermlinkHighlighter())

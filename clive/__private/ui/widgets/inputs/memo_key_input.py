from __future__ import annotations

from re import Pattern, compile
from typing import TYPE_CHECKING, Final

from rich.highlighter import Highlighter

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import KEY_PLACEHOLDER

if TYPE_CHECKING:
    from rich.text import Text


class MemoKeyHighlighter(Highlighter):
    HIVE_MEMO_KEY_REGEX: Final[Pattern[str]] = compile(
        r"^(?:STM|TST)[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{7,51}$"
    )

    @classmethod
    def is_valid_memo_keys(cls, memo_key: str) -> bool:
        return cls.HIVE_MEMO_KEY_REGEX.match(memo_key) is not None

    def highlight(self, text: Text) -> None:
        if self.is_valid_memo_keys(str(text)):
            text.stylize("green")
        else:
            text.stylize("red")


class MemoKeyInput(TextInput):
    def __init__(self, label: str = "memo key", placeholder: str = KEY_PLACEHOLDER, value: str | None = None):
        super().__init__(label=label, placeholder=placeholder, value=value)

from __future__ import annotations

from re import Pattern, compile
from typing import TYPE_CHECKING, Final

from rich.highlighter import Highlighter

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_NAME_PLACEHOLDER

if TYPE_CHECKING:
    from rich.text import Text
    from textual.widget import Widget


class AccountNameHighlighter(Highlighter):
    MAX_ACCOUNT_NAME_LENGTH: Final[int] = 14
    HIVE_ACCOUNT_NAME_REGEX: Final[Pattern[str]] = compile(
        r"^((([a-z0-9])[a-z0-9\-]{1,14}([a-z0-9]))(\.([a-z0-9])[a-z0-9\-]{1,14}([a-z0-9]))*)$"
    )

    @classmethod
    def is_valid_account_name(cls, name: str) -> bool:
        return len(name) <= cls.MAX_ACCOUNT_NAME_LENGTH and (cls.HIVE_ACCOUNT_NAME_REGEX.match(name) is not None)

    def highlight(self, text: Text) -> None:
        if self.is_valid_account_name(str(text)):
            text.stylize("green")
        else:
            text.stylize("red")


class AccountNameInput(TextInput):
    def __init__(
        self,
        to_mount: Widget,
        label: str = "account name",
        placeholder: str = ACCOUNT_NAME_PLACEHOLDER,
        value: str | None = None,
        id_: str | None = None,
    ) -> None:
        super().__init__(
            to_mount=to_mount,
            label=label,
            placeholder=placeholder,
            value=value,
            highlighter=AccountNameHighlighter(),
            id_=id_,
        )

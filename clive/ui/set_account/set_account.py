from __future__ import annotations

from re import compile
from typing import TYPE_CHECKING, Final, Pattern

from rich.highlighter import Highlighter
from textual.binding import Binding
from textual.widgets import Input, Label

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.shared.form_screen import FormScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.notification import Notification
from clive.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from rich.text import Text
    from textual.app import ComposeResult


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


class SetAccount(BaseScreen, FormScreen):
    BINDINGS = [Binding("f10", "save_account_name", "Save")]

    def __init__(self) -> None:
        super().__init__()

        self.__account_name_input = Input(
            str(self.app.profile_data.active_account.name),
            placeholder="e.g.: cookingwithkasia",
            id="set_account_name",
            highlighter=AccountNameHighlighter(),
        )

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("set account name")
            yield Label("Account name:\t @")
            yield self.__account_name_input

    def action_save_account_name(self) -> None:
        account_name = self.__account_name_input.value
        if not AccountNameHighlighter.is_valid_account_name(account_name):
            Notification("Invalid account name!", category="error").show()
            return

        self.app.profile_data.active_account.name = account_name
        self.app.profile_data.save()
        self._owner.action_next_screen()
        Notification("Account name saved.", category="success").show()

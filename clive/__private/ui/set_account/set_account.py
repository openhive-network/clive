from __future__ import annotations

from re import Pattern, compile
from typing import TYPE_CHECKING, Final

from rich.highlighter import Highlighter
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import Checkbox, Input, Static

from clive.__private.core.profile_data import ProfileData
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.exceptions import FormValidationError

if TYPE_CHECKING:
    from rich.text import Text
    from textual.app import ComposeResult

    from clive.__private.ui.shared.form import Form


class InvalidAccountNameError(FormValidationError):
    def __init__(self, given_account_name: str) -> None:
        super().__init__(f"Given account name is invalid: `{given_account_name}`", given_value=given_account_name)


class ScrollablePart(ScrollableContainer):
    """All the content of the screen, excluding the title."""


class AccountNameInputContainer(Horizontal):
    """Container for account name input and label."""


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


class SetAccount(BaseScreen, FormScreen[ProfileData]):
    def __init__(self, owner: Form[ProfileData]) -> None:
        super().__init__(owner)

        self.__account_name_input = Input(
            str(self.context.working_account.name),
            placeholder="Please enter hive account name, without @",
            id="set_account_name",
            highlighter=AccountNameHighlighter(),
        )

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("set account name")
            with ScrollablePart():
                with AccountNameInputContainer():
                    yield Static("Account name:", id="account-name-label")
                    yield Static("@", id="account-name-at")
                    yield self.__account_name_input
                yield Checkbox("Working account?", value=True)

    def apply_and_validate(self) -> None:
        if not AccountNameHighlighter.is_valid_account_name(account_name := self.__account_name_input.value):
            raise InvalidAccountNameError(account_name)

        self.context.working_account.name = account_name

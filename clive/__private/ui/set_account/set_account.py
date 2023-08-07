from __future__ import annotations

from typing import TYPE_CHECKING

from rich.highlighter import Highlighter
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import Checkbox, Input, Static

from clive.__private.core.profile_data import ProfileData
from clive.__private.storage.accounts import Account, InvalidAccountNameError, WorkingAccount
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.exceptions import FormValidationError

if TYPE_CHECKING:
    from rich.text import Text
    from textual.app import ComposeResult

    from clive.__private.ui.shared.form import Form


class ScrollablePart(ScrollableContainer):
    """All the content of the screen, excluding the title."""


class AccountNameInputContainer(Horizontal):
    """Container for account name input and label."""


class AccountNameHighlighter(Highlighter):
    def highlight(self, text: Text) -> None:
        text.stylize("green" if Account.is_valid(str(text)) else "red")


class SetAccount(BaseScreen, FormScreen[ProfileData]):
    def __init__(self, owner: Form[ProfileData]) -> None:
        super().__init__(owner)

        self.__account_name_input = Input(
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
        account_name = self.__account_name_input.value
        try:
            Account.validate(account_name)
        except InvalidAccountNameError as error:
            raise FormValidationError(str(error), given_value=account_name) from error

        self.context.working_account = WorkingAccount(name=account_name)

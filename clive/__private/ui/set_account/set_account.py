from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import ScrollableContainer
from textual.widgets import Checkbox

from clive.__private.core.profile_data import ProfileData
from clive.__private.storage.accounts import Account, InvalidAccountNameError, WorkingAccount
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.exceptions import FormValidationError

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.shared.form import Form


class ScrollablePart(ScrollableContainer):
    """All the content of the screen, excluding the title."""


class SetAccount(BaseScreen, FormScreen[ProfileData]):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, owner: Form[ProfileData]) -> None:
        super().__init__(owner)

        self.__account_name_input = AccountNameInput(placeholder="Please enter hive account name, without @")

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("set account name")
            with ScrollablePart():
                yield self.__account_name_input
                yield Checkbox("Working account?", value=True)

    async def apply_and_validate(self) -> None:
        account_name = self.__account_name_input.value
        try:
            Account.validate(account_name)
        except InvalidAccountNameError as error:
            raise FormValidationError(str(error), given_value=account_name) from error

        if self.__is_working_account():
            self.context.working_account = WorkingAccount(name=account_name)
            self.context.watched_accounts.clear()
        else:
            self.context._working_account = None
            self.context.watched_accounts.add(Account(name=account_name))

    def __is_working_account(self) -> bool:
        return self.query_one(Checkbox).value

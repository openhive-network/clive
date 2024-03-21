from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Checkbox

from clive.__private.core.commands.find_accounts import AccountNotFoundError
from clive.__private.core.profile_data import ProfileData
from clive.__private.storage.accounts import Account
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInputError
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.exceptions import FormValidationError

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.shared.form import Form


class WorkingAccountCheckbox(Checkbox):
    def __init__(self) -> None:
        super().__init__("Working account?", value=True)


class SetAccount(BaseScreen, FormScreen[ProfileData]):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, owner: Form[ProfileData]) -> None:
        super().__init__(owner)

        self._account_name_input = AccountNameInput(
            placeholder="Please enter hive account name, without @", include_title_in_placeholder_when_blurred=False
        )
        self._working_account_checkbox = WorkingAccountCheckbox()

    def create_main_panel(self) -> ComposeResult:
        yield BigTitle("set account name")
        with ScrollablePart():
            yield self._account_name_input
            yield self._working_account_checkbox

    async def apply_and_validate(self) -> None:
        try:
            account_name = self._account_name_input.value_or_error
        except CliveValidatedInputError as error:
            raise FormValidationError(str(error)) from error

        if not await self._does_account_exist_in_node(account_name):
            raise FormValidationError(f"Account {account_name} does not exist in the node.")

        if self.__is_working_account():
            self.context.set_working_account(account_name)
            self.context.watched_accounts.clear()
        else:
            self.context.unset_working_account()
            self.context.watched_accounts.add(Account(name=account_name))

    async def _does_account_exist_in_node(self, account_name: str) -> bool:
        try:
            wrapper = await self.app.world.commands.find_accounts(accounts=[account_name])
        except AccountNotFoundError:
            return False
        else:
            return wrapper.success

    def __is_working_account(self) -> bool:
        return self.query_one(WorkingAccountCheckbox).value

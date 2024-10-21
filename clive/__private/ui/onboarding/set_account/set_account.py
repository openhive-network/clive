from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Checkbox

from clive.__private.core.constants.tui.placeholders import ACCOUNT_NAME_ONBOARDING_PLACEHOLDER
from clive.__private.core.profile import Profile
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.onboarding.form_screen import FormScreen
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.clive_validated_input import FailedValidationError
from clive.__private.ui.widgets.section import SectionScrollable

if TYPE_CHECKING:
    from textual.app import ComposeResult


class WorkingAccountCheckbox(Checkbox):
    def __init__(self) -> None:
        super().__init__("Working account?", value=True)


class SetAccount(BaseScreen, FormScreen[Profile]):
    CSS_PATH = [get_relative_css_path(__file__)]
    BIG_TITLE = "onboarding"

    @property
    def account_name(self) -> str:
        """
        The account name that was entered.

        Raises:
            FailedValidationError: If the account name is not valid.
        """
        return self.query_exactly_one(AccountNameInput).value_or_error

    @property
    def should_be_working_account(self) -> bool:
        return self.query_exactly_one(WorkingAccountCheckbox).value

    def create_main_panel(self) -> ComposeResult:
        with SectionScrollable("Set account name"):
            yield AccountNameInput(
                placeholder=ACCOUNT_NAME_ONBOARDING_PLACEHOLDER,
                include_title_in_placeholder_when_blurred=False,
                show_known_account=False,
            )
            yield WorkingAccountCheckbox()

    async def validate(self) -> SetAccount.ValidationFail | None:
        try:
            account_name = self.account_name
        except FailedValidationError:
            return self.ValidationFail()

        wrapper = await self.commands.does_account_exists_in_node(account_name=account_name)
        if wrapper.error_occurred:
            return self.ValidationFail(f"Failed to check if account {account_name} exists in the node.")

        if not wrapper.result_or_raise:
            return self.ValidationFail(f"Account {account_name} does not exist in the node.")
        return None

    async def apply(self) -> None:
        # allow only for adding one account
        self.context.accounts.unset_working_account()
        self.context.accounts.watched.clear()
        self.context.accounts.known.clear()

        account_name = self.account_name

        self.context.accounts.known.add(account_name)
        if self.should_be_working_account:
            self.context.accounts.set_working_account(account_name)
        else:
            self.context.accounts.watched.add(account_name)

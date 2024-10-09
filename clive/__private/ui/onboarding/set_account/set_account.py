from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.widgets import Checkbox

from clive.__private.core.constants.tui.placeholders import ACCOUNT_NAME_ONBOARDING_PLACEHOLDER
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.onboarding.navigation_buttons import (
    FINISH_ONBOARDING_BUTTON_LABEL,
    NavigationButtons,
    NextScreenButton,
)
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.form_screen import FinishOnboardingFormScreen
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.clive_input import CliveInput
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInputError
from clive.__private.ui.widgets.section import SectionScrollable
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint
from clive.exceptions import FormValidationError

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.profile import Profile
    from clive.__private.ui.onboarding.form import Form


class WorkingAccountCheckbox(Checkbox):
    def __init__(self) -> None:
        super().__init__("Working account?", value=True)


class SetAccount(BaseScreen, FinishOnboardingFormScreen):
    CSS_PATH = [get_relative_css_path(__file__)]
    BIG_TITLE = "create profile"

    def __init__(self, owner: Form[Profile]) -> None:
        super().__init__(owner)

        self._account_name_input = AccountNameInput(
            placeholder=ACCOUNT_NAME_ONBOARDING_PLACEHOLDER,
            include_title_in_placeholder_when_blurred=False,
            show_known_account=False,
        )
        self._working_account_checkbox = WorkingAccountCheckbox()

    def create_main_panel(self) -> ComposeResult:
        with SectionScrollable("Set account name"):
            yield self._account_name_input
            yield self._working_account_checkbox
            yield NavigationButtons()
        yield SelectCopyPasteHint()

    def on_mount(self) -> None:
        self.watch(self._working_account_checkbox, "value", self._change_next_screen_button_label)

    async def apply_and_validate(self) -> None:
        try:
            account_name = self._account_name_input.value_or_error
        except CliveValidatedInputError as error:
            raise FormValidationError(str(error)) from error

        wrapper = await self.commands.does_account_exists_in_node(account_name=account_name)
        if wrapper.error_occurred:
            raise FormValidationError(f"Failed to check if account {account_name} exists in the node.")

        if not wrapper.result_or_raise:
            raise FormValidationError(f"Account {account_name} does not exist in the node.")

        # allow only for adding one account
        self.context.accounts.watched.clear()
        self.context.accounts.known.clear()
        self.context.accounts.unset_working_account()

        self.context.accounts.known.add(account_name)
        if self._working_account_checkbox.value:
            self.context.accounts.set_working_account(account_name)
        else:
            self.context.accounts.watched.add(account_name)

    @on(CliveInput.Submitted)
    @on(NextScreenButton.Pressed)
    async def action_next_screen(self) -> None:
        try:
            await self.apply_and_validate()
        except FormValidationError:
            pass  # handled in the super class
        else:
            if not self.context.accounts.has_working_account:
                await self.action_finish()
            else:
                await super().action_next_screen()

    def _change_next_screen_button_label(self) -> None:
        if self._working_account_checkbox.value:
            self.query_one(NextScreenButton).label = NextScreenButton.DEFAULT_NEXT_BUTTON_LABEL
            return
        self.query_one(NextScreenButton).label = FINISH_ONBOARDING_BUTTON_LABEL

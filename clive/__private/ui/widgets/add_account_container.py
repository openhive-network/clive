from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.section import Section
from clive.__private.validators.set_known_account_validator import SetKnownAccountValidator
from clive.__private.validators.set_tracked_account_validator import SetTrackedAccountValidator

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.screens.settings.account_management.common.manage_accounts_table import AccountsType


class AddAccountContainer(Horizontal, CliveWidget):
    DEFAULT_CSS = """
    AddAccountContainer {
        height: auto;
    }
    """

    def __init__(
        self,
        accounts_type: AccountsType,
        *,
        show_section_title: bool = True,
    ) -> None:
        super().__init__()
        self._account_input = AccountNameInput(
            required=False,
            validators=(
                SetTrackedAccountValidator(self.profile)
                if accounts_type == "tracked_accounts"
                else SetKnownAccountValidator(self.profile)
            ),
            show_known_account=accounts_type != "known_accounts",
        )
        self._accounts_type = accounts_type
        self._show_section_title = show_section_title

    def compose(self) -> ComposeResult:
        section_title = (
            f"{'Add tracked account' if self._accounts_type == 'tracked_accounts' else 'Add known account'}"
            if self._show_section_title
            else ""
        )
        with Section(section_title):
            yield self._account_input

    async def save_account(self) -> bool:
        """
        Save the account to the profile.

        Returns:
            True if the account was saved, False otherwise.
        """
        if not self._account_input.validate_passed():
            return False

        account_name = self._account_input.value_or_error
        if not await self.app.does_account_exist_in_node(account_name=account_name):
            return False

        if self._accounts_type == "tracked_accounts":
            self.profile.accounts.add_tracked_account(account_name)
        else:
            self.profile.accounts.known.add(account_name)

        self.app.trigger_profile_watchers()
        self._account_input.input.clear()
        self.app.update_alarms_data()
        return True

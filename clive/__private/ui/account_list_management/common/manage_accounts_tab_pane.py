from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.widgets import TabPane

from clive.__private.storage.accounts import Account
from clive.__private.ui.account_list_management.common.manage_accounts_table import AccountsType, ManageAccountsTable
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section import Section
from clive.__private.validators.set_known_account_validator import SetKnownAccountValidator
from clive.__private.validators.set_tracked_account_validator import SetTrackedAccountValidator

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ManageAccountsTabPane(TabPane, CliveWidget):
    """TabPane used to add and delete watched or known accounts."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: str, accounts_type: AccountsType) -> None:
        super().__init__(title=title)
        self._accounts_input = AccountNameInput(
            required=False,
            validators=(
                SetTrackedAccountValidator(self.app.world.profile_data)
                if accounts_type == "tracked_accounts"
                else SetKnownAccountValidator(self.app.world.profile_data)
            ),
            ask_known_account=accounts_type != "known_accounts",
        )
        self._accounts_type = accounts_type

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            with Section(f"{'Track' if self._accounts_type == 'tracked_accounts' else 'Add known'} account"):
                yield self._accounts_input
                yield CliveButton(
                    "Add",
                    variant="success",
                    id_="save-account-button",
                )

            yield ManageAccountsTable(self._accounts_type)

    @on(CliveButton.Pressed, "#save-account-button")
    async def save_account(self) -> None:
        if not self._accounts_input.validate_passed():
            return

        account_name = self._accounts_input.value_or_error
        wrapper = await self.app.world.commands.does_account_exists_in_node(account_name=account_name)
        if wrapper.error_occurred:
            self.notify(f"Failed to check if account {account_name} exists in the node.", severity="warning")
            return

        if not wrapper.result_or_raise:
            self.notify(f"Account {account_name} does not exist in the node.", severity="warning")
            return

        account = Account(name=self._accounts_input.value_or_error)

        if self._accounts_type == "tracked_accounts":
            self.app.world.profile_data.watched_accounts.add(account)
        else:
            self.app.world.profile_data.known_accounts.add(account)
        self.app.trigger_profile_data_watchers()
        self._accounts_input.input.clear()
        self.app.update_alarms_data_asap()

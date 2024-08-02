from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal

from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.section import Section
from clive.__private.validators.set_known_account_validator import SetKnownAccountValidator
from clive.__private.validators.set_tracked_account_validator import SetTrackedAccountValidator

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.account_list_management.common.manage_accounts_table import AccountsType


class AddAccountContainer(Horizontal, CliveWidget):
    DEFAULT_CSS = """
    AddAccountContainer {
        height: auto;

        #buttons-container {
            align: center middle;
            height: auto;
            width: 1fr;
            margin-top: 1;

            CliveButton {
                margin: 0 2 0 2;
                width: 1fr;
            }
        }

        #button-container {
            height: auto;
            width: auto;
        }
    }
    """

    def __init__(self, accounts_type: AccountsType, *, with_cancel_button: bool = False) -> None:
        super().__init__()
        self._account_input = AccountNameInput(
            required=False,
            validators=(
                SetTrackedAccountValidator(self.profile_data)
                if accounts_type == "tracked_accounts"
                else SetKnownAccountValidator(self.profile_data)
            ),
            ask_known_account=accounts_type != "known_accounts",
        )
        self._accounts_type = accounts_type
        self._with_cancel_button = with_cancel_button

    def compose(self) -> ComposeResult:
        with Section(f"{'Track' if self._accounts_type == 'tracked_accounts' else 'Add known'} account"):
            yield self._account_input
            with Horizontal(id="buttons-container" if self._with_cancel_button else "button-container"):
                yield CliveButton(
                    "Add",
                    variant="success",
                    id_="save-account-button",
                )
                if self._with_cancel_button:
                    yield CliveButton(
                        "Cancel",
                        variant="error",
                        id_="cancel-button",
                    )

    @on(CliveButton.Pressed, "#save-account-button")
    async def save_account(self) -> None:
        if not self._account_input.validate_passed():
            return

        account_name = self._account_input.value_or_error
        wrapper = await self.commands.does_account_exists_in_node(account_name=account_name)
        if wrapper.error_occurred:
            self.notify(f"Failed to check if account {account_name} exists in the node.", severity="warning")
            return

        if not wrapper.result_or_raise:
            self.notify(f"Account {account_name} does not exist in the node.", severity="warning")
            return

        if self._accounts_type == "tracked_accounts":
            self.profile_data.accounts.watched.add(account_name)
        else:
            self.profile_data.accounts.known.add(account_name)
        self.app.trigger_profile_data_watchers()
        self._account_input.input.clear()
        if self._with_cancel_button:
            self.app.pop_screen()
        self.app.update_alarms_data_asap()

from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Center, Vertical

from clive.__private.ui.widgets.buttons import OneLineButton
from clive.__private.ui.widgets.notice import Notice

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AccountManagementReference(Vertical):
    DEFAULT_CSS = """
    AccountManagementReference {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Notice("For more advanced management, go to:", variant="grey")
        with Center():
            yield OneLineButton("Account management", id_="account-management-button")

    @on(OneLineButton.Pressed, "#account-management-button")
    def push_account_list_management_screen(self) -> None:
        from clive.__private.ui.screens.settings.account_management import AccountManagement  # noqa: PLC0415

        self.app.push_screen(AccountManagement())

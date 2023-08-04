from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.widgets import Checkbox, Input

from clive.__private.storage.accounts import Account
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult


class KnownAccount(CliveWidget):
    def __init__(self, input_: Input):
        self.input = input_
        self.checkbox = Checkbox("Known account?", disabled=True)
        super().__init__()

    @property
    def account_name_raw(self) -> str:
        return self.input.value

    @property
    def account(self) -> Account:
        """
        Get the account from the input.

        Raises
        ------
        InvalidAccountNameError: if the given account name is invalid.
        """
        return Account(self.account_name_raw)

    def on_mount(self) -> None:
        self.watch(self.input, "value", self.__input_changed)

    def compose(self) -> ComposeResult:
        yield self.checkbox

    @on(Checkbox.Changed)
    def update_known_accounts(self, event: Checkbox.Changed) -> None:
        if not self.__is_account_name_valid():
            return

        checked = event.value
        if checked:
            self.app.world.profile_data.known_accounts.add(self.account)
        else:
            self.app.world.profile_data.known_accounts.discard(self.account)

    def __input_changed(self) -> None:
        self.checkbox.disabled = not self.__is_account_name_valid()
        self.checkbox.value = self.__is_account_name_valid() and self.__is_given_account_known()

    def __is_account_name_valid(self) -> bool:
        return Account.is_valid(self.account_name_raw)

    def __is_given_account_known(self) -> bool:
        return self.account in self.app.world.profile_data.known_accounts

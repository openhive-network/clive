from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual import on
from textual.message import Message
from textual.widgets import Checkbox, Input

from clive.__private.core.accounts.accounts import KnownAccount as KnownAccountModel
from clive.__private.ui.widgets.clive_basic.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.accounts.account_manager import AccountManager


class KnownAccount(CliveWidget):
    @dataclass
    class Status(Message):
        """Posted when the known account status changes."""

        is_account_known: bool
        account_name: str
        """A valid account name."""

    class Disabled(Message):
        """Posted when the widget is going to the disabled state. (e.g. account name is invalid so can't be known)."""

    def __init__(self, input: Input, accounts_holder: AccountManager | None = None) -> None:  # noqa: A002
        """
        Initialize the widget.

        Args:
        ----
        input: The input widget to get the account name from.
        accounts_holder: Object that holds known accounts. If not provided, the account holder from app world is used.
        """
        self.input = input
        self._account_holder = accounts_holder if accounts_holder is not None else self.profile.accounts

        self.checkbox = Checkbox("Known?", disabled=True)
        super().__init__()

    @property
    def account_name_raw(self) -> str:
        return self.input.value

    @property
    def account(self) -> KnownAccountModel:
        """
        Get the account from the input.

        Raises:  # noqa: D406
        ------
        InvalidAccountNameError: if the given account name is invalid.
        """
        return KnownAccountModel(self.account_name_raw)

    def on_mount(self) -> None:
        # >>> start workaround for Textual calling validate on input when self.watch is used. Setting validate_on to
        # values different from "changed" prevents this.
        before = self.input.validate_on
        self.input.validate_on = ["blur"]

        self.watch(self.input, "value", self.__input_changed)

        self.input.validate_on = before
        # <<< end workaround

        self.watch(self.checkbox, "disabled", self.__post_disabled)

    def compose(self) -> ComposeResult:
        yield self.checkbox

    @on(Checkbox.Changed)
    def update_known_accounts(self, event: Checkbox.Changed) -> None:
        if not self.__is_account_name_valid():
            return

        checked = event.value
        if checked:
            self._account_holder.known.add(self.account)
        else:
            self._account_holder.known.remove(self.account)

        self.post_message(self.Status(is_account_known=checked, account_name=self.account_name_raw))

    def __input_changed(self) -> None:
        valid = self.__is_account_name_valid()
        is_account_known = self.__should_check_as_known()

        self.checkbox.disabled = not valid
        with self.app.prevent(Checkbox.Changed):
            self.checkbox.value = is_account_known

        if valid:
            self.post_message(self.Status(is_account_known=is_account_known, account_name=self.account_name_raw))

    def __post_disabled(self, disabled: bool) -> None:  # noqa: FBT001
        if disabled:
            self.post_message(self.Disabled())

    def __is_account_name_valid(self) -> bool:
        return KnownAccountModel.is_valid(self.account_name_raw)

    def __is_given_account_known(self) -> bool:
        return self._account_holder.is_account_known(self.account)

    def __should_check_as_known(self) -> bool:
        return self.__is_account_name_valid() and self.__is_given_account_known()

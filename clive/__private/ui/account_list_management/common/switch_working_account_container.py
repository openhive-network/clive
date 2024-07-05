from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import RadioSet, Static

from clive.__private.storage.accounts import Account, WorkingAccount
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.styling import colorize_shortcut
from clive.__private.ui.widgets.clive_radio_button import CliveRadioButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.section import Section, SectionBody

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AccountRadioButton(CliveRadioButton):
    WORKING_ACCOUNT_IDENTIFIER: Final[str] = colorize_shortcut("(working)")

    def __init__(self, account: Account) -> None:
        is_working = isinstance(account, WorkingAccount)
        super().__init__(
            label=f"{account.name}{ self.WORKING_ACCOUNT_IDENTIFIER if is_working else ''}",
            value=is_working,
            id=self.get_button_id(account.name),
        )
        self.account = account

    @staticmethod
    def get_button_id(account_name: str, *, to_query: bool = False) -> str:
        if not to_query:
            return f"radio-button-{account_name}"
        return f"#radio-button-{account_name}"

    def remove_working_account_label(self) -> None:
        self.label = self.account.name  # type: ignore[assignment]

    def add_working_account_label(self) -> None:
        self.label = f"{self.account.name} {self.WORKING_ACCOUNT_IDENTIFIER}"  # type: ignore[assignment]


class NoTrackedAccounts(NoContentAvailable):
    NO_TRACKED_ACCOUNTS_MESSAGE: Final[str] = "You have no tracked accounts"

    def __init__(self) -> None:
        super().__init__(self.NO_TRACKED_ACCOUNTS_MESSAGE)


class NoWorkingAccountSelected:
    """Class using to indicate that no working account is selected."""


class SwitchWorkingAccountContainer(Container, CliveWidget):
    """
    Container that displays all tracked accounts (working + watched) and allows to switch between them.

    Notice:
    -------
    Using radio set in this container requires the use of `AccountRadioButton`,
    otherwise it will raise an AssertionError.
    """

    _tracked_accounts: reactive[list[Account] | None] = reactive(None)
    """Reactive, which triggers the rebuilding of the radio set containing the tracked accounts to switch between."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, *, show_title: bool = True, dynamic: bool = False) -> None:
        super().__init__()
        self._show_title = show_title
        self._selected_account: Account | NoWorkingAccountSelected = NoWorkingAccountSelected()
        self._dynamic = dynamic

    def on_mount(self) -> None:
        if self.app.world.profile_data.is_working_account_set():
            self._selected_account = self.app.world.profile_data.working_account

        if self._dynamic:

            def delegate_work() -> None:
                self.run_worker(self._update_tracked_accounts())

            self.watch(self.app.world, "profile_data", delegate_work)

        self._tracked_accounts = self.app.world.profile_data.tracked_accounts_sorted

    async def _update_tracked_accounts(self) -> None:
        self._tracked_accounts = self.app.world.profile_data.tracked_accounts_sorted

    def watch__tracked_accounts(self, tracked_accounts: list[Account] | None) -> None:
        if tracked_accounts is None:
            return

        with self.app.batch_update():
            self.query_one(SectionBody).query("*").remove()
            self._mount_tracked_accounts_content(tracked_accounts)

    def compose(self) -> ComposeResult:
        with Section("Switch working account" if self._show_title else None):
            if self._tracked_accounts is None:
                yield Static("Loading...")
                return

            if not self._tracked_accounts:
                yield NoTrackedAccounts()
                return

            with RadioSet():
                yield from self._create_tracked_accounts_buttons(self._tracked_accounts)

    def _mount_tracked_accounts_content(self, tracked_accounts: list[Account]) -> None:
        section_body = self.query_one(SectionBody)
        if not tracked_accounts:
            section_body.mount(NoTrackedAccounts())
            return

        self.query_one(SectionBody).mount(RadioSet(*self._create_tracked_accounts_buttons(tracked_accounts)))

    def _create_tracked_accounts_buttons(
        self, tracked_accounts: list[Account]
    ) -> list[AccountRadioButton | CliveRadioButton]:
        """
        Create radio buttons for all tracked accounts and a no working account button.

        `No working account` button is created because the textual `RadioSet` does not support deselecting radio buttons
        and situations where there are no radio buttons selected. This approach is not ideal, but this way we do not
        have to change the `RadioSet` code.
        """
        return [AccountRadioButton(account) for account in tracked_accounts] + [
            CliveRadioButton(
                "(no working account)",
                value=not self.app.world.profile_data.is_working_account_set(),
                id="no-working-account-button",
            )
        ]

    @on(RadioSet.Changed)
    def change_selected_working_account(self, event: RadioSet.Changed) -> None:
        if not isinstance(event.pressed, AccountRadioButton):
            # There is only one case where the `AccountRadioButton` is not used - when a working account is removed
            self._update_selected_account(NoWorkingAccountSelected())
            return

        assert isinstance(event.pressed, AccountRadioButton), (
            "Expected AccountRadioButton, " "got CliveRadioButton or RadioButton"
        )

        if self._selected_account == event.pressed.account:
            return

        self._update_selected_account(event.pressed.account)

    def confirm_selected_working_account(self) -> None:
        if self._is_no_working_account_selected and not self.app.world.profile_data.is_working_account_set():
            return

        if self._is_current_working_account_selected:
            return

        if self._is_no_working_account_selected:
            self.app.world.profile_data.move_working_account_to_watched()
            self._perform_actions_after_accounts_modification()
            return

        if self.app.world.profile_data.is_working_account_set():
            self.app.world.profile_data.move_working_account_to_watched()

        self.app.world.profile_data.set_watched_account_as_working(self._selected_account)  # type: ignore[arg-type]
        self._perform_actions_after_accounts_modification()

    def _update_selected_account(self, account: Account | NoWorkingAccountSelected) -> None:
        if not isinstance(self._selected_account, NoWorkingAccountSelected):
            self.query_one(
                AccountRadioButton.get_button_id(self._selected_account.name, to_query=True), AccountRadioButton
            ).remove_working_account_label()

        self._selected_account = account

        if not isinstance(account, NoWorkingAccountSelected):
            self.query_one(
                AccountRadioButton.get_button_id(account.name, to_query=True), AccountRadioButton
            ).add_working_account_label()
            return

    def _perform_actions_after_accounts_modification(self) -> None:
        self.app.trigger_profile_data_watchers()
        self.app.update_alarms_data_asap()

    @property
    def _is_current_working_account_selected(self) -> bool:
        return (
            self.app.world.profile_data.is_working_account_set()
            and not isinstance(self._selected_account, NoWorkingAccountSelected)
            and self.app.world.profile_data.working_account.name == self._selected_account.name
        )

    @property
    def _is_no_working_account_selected(self) -> bool:
        return isinstance(self._selected_account, NoWorkingAccountSelected)

from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal
from textual.widgets import Label, Static, TabPane

from clive.__private.storage.accounts import Account
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_checkerboard_table import (
    EVEN_CLASS_NAME,
    ODD_CLASS_NAME,
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.profile_data import ProfileData
    from clive.__private.core.world import TextualWorld


class KnownAccountsTableHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Label("Known account", classes=ODD_CLASS_NAME)
        yield Label("Action", classes=EVEN_CLASS_NAME)


class KnownAccount(CliveCheckerboardTableRow, CliveWidget):
    def __init__(self, known_account: Account):
        super().__init__(
            CliveCheckerBoardTableCell(known_account.name),
            CliveCheckerBoardTableCell(CliveButton("Mark as unknown", variant="error", id_="unknown-account-button")),
        )
        self._known_account = known_account

    @on(CliveButton.Pressed, "#unknown-account-button")
    def mark_account_as_unknown(self) -> None:
        self.app.world.profile_data.known_accounts.discard(self._known_account)


class KnownAccountsTable(CliveCheckerboardTable):
    def __init__(self) -> None:
        super().__init__(
            Static("Mark account(s) as unknown", id="manage-known-accounts-title"),
            KnownAccountsTableHeader(),
            dynamic=True,
            attr_to_watch="profile_data",
        )
        self._previous_known_accounts_names: list[str] | None = None

    def create_dynamic_rows(self, content: ProfileData) -> list[KnownAccount]:
        self._previous_known_accounts_names = [known_account.name for known_account in content.known_accounts]

        return [KnownAccount(known_account) for known_account in content.known_accounts]

    def get_no_content_available_widget(self) -> Static:
        return Static("You have no known accounts", id="no-known-accounts-info")

    @property
    def check_if_should_be_updated(self) -> bool:
        return [
            known_account.name for known_account in self.app.world.profile_data.known_accounts
        ] != self._previous_known_accounts_names

    @property
    def is_anything_to_display(self) -> bool:
        return len(self.object_to_watch.profile_data.known_accounts) != 0

    @property
    def object_to_watch(self) -> TextualWorld:
        return self.app.world


class KnownAccounts(TabPane, CliveWidget):
    """TabPane used to add and delete known accounts."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: str):
        super().__init__(title=title)
        self._known_account_input = AccountNameInput()

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield SectionTitle("Mark account as known")
            with Horizontal(id="input-with-button"):
                yield self._known_account_input
                yield CliveButton("mark as known!", variant="success", id_="known-account-button")
            yield KnownAccountsTable()

    @on(CliveButton.Pressed, "#known-account-button")
    def mark_account_as_known(self) -> None:
        if not self._known_account_input.validate_passed():
            return

        known_account = Account(name=self._known_account_input.value_or_error)

        if known_account in self.app.world.profile_data.known_accounts:
            self.notify("This account is already known!", severity="warning")
            return

        self.app.world.profile_data.known_accounts.add(known_account)

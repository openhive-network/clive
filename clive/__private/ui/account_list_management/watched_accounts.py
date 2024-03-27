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


class WatchedAccountsTableHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Label("Watched account", classes=ODD_CLASS_NAME)
        yield Label("Action", classes=EVEN_CLASS_NAME)


class WatchedAccount(CliveCheckerboardTableRow, CliveWidget):
    def __init__(self, watched_account: Account):
        super().__init__(
            CliveCheckerBoardTableCell(watched_account.name),
            CliveCheckerBoardTableCell(CliveButton("Unwatch", variant="error", id_="unwatch-account-button")),
        )
        self._watched_account = watched_account

    @on(CliveButton.Pressed, "#unwatch-account-button")
    def unwatch_account(self) -> None:
        self.app.world.profile_data.watched_accounts.discard(self._watched_account)


class WatchedAccountsTable(CliveCheckerboardTable):
    def __init__(self) -> None:
        super().__init__(
            Static("Unwatch account(s)", id="manage-watched-accounts-title"),
            WatchedAccountsTableHeader(),
            dynamic=True,
            attr_to_watch="profile_data",
        )
        self._previous_watched_account_names: list[str] | None = None

    def create_dynamic_rows(self, content: ProfileData) -> list[WatchedAccount]:
        self._previous_watched_account_names = [watched_account.name for watched_account in content.watched_accounts]

        return [WatchedAccount(watched_account) for watched_account in content.watched_accounts]

    def get_no_content_available_widget(self) -> Static:
        return Static("You have no watched accounts", id="no-watched-accounts-info")

    @property
    def check_if_should_be_updated(self) -> bool:
        return [
            watched_account.name for watched_account in self.app.world.profile_data.watched_accounts
        ] != self._previous_watched_account_names

    @property
    def is_anything_to_display(self) -> bool:
        return len(self.object_to_watch.profile_data.watched_accounts) != 0

    @property
    def object_to_watch(self) -> TextualWorld:
        return self.app.world


class WatchedAccounts(TabPane, CliveWidget):
    """TabPane used to add and delete watched accounts."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: str):
        super().__init__(title=title)
        self._watch_account_input = AccountNameInput()

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield SectionTitle("Watch account")
            with Horizontal(id="input-with-button"):
                yield self._watch_account_input
                yield CliveButton("watch!", variant="success", id_="watch-account-button")
            yield WatchedAccountsTable()

    @on(CliveButton.Pressed, "#watch-account-button")
    def watch_account(self) -> None:
        if not self._watch_account_input.validate_passed():
            return

        watched_account = Account(name=self._watch_account_input.value_or_error)

        if watched_account in self.app.world.profile_data.watched_accounts:
            self.notify("This account is already watched!", severity="warning")
            return

        self.app.world.profile_data.watched_accounts.add(watched_account)

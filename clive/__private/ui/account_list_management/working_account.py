from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, TabPane

from clive.__private.ui.account_list_management.common.header_of_tables import AccountsTableHeader
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_checkerboard_table import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.one_line_button import OneLineButton
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.profile_data import ProfileData
    from clive.__private.core.world import TextualWorld
    from clive.__private.storage.accounts import Account
    from clive.__private.storage.accounts import WorkingAccount as WorkingAccountType


def _has_working_account(profile_data: ProfileData) -> bool:
    return profile_data.is_working_account_set()


class RemoveWorkingAccount(CliveCheckerboardTableRow, CliveWidget):
    def __init__(self, working_account: Account):
        super().__init__(
            CliveCheckerBoardTableCell(working_account.name),
            CliveCheckerBoardTableCell(OneLineButton("Remove", variant="error", id_="remove-working-account-button")),
        )

    @on(CliveButton.Pressed, "#remove-working-account-button")
    def remove_working_account(self) -> None:
        self.app.world.profile_data.unset_working_account()
        self.app.trigger_profile_data_watchers()


class ManageWorkingAccountTable(CliveCheckerboardTable):
    ATTRIBUTE_TO_WATCH = "profile_data"

    def __init__(self) -> None:
        super().__init__(
            Static("Your working account", id="manage-working-account-title"),
            AccountsTableHeader(),
        )
        self._previous_working_account: str | None = ""
        # Initialize via empty string to trigger the first update, later when no working account it will be set to None

    def create_dynamic_rows(self, content: ProfileData) -> list[RemoveWorkingAccount]:
        self._previous_working_account = content.working_account.name if _has_working_account(content) else None

        return [RemoveWorkingAccount(self.app.world.profile_data.working_account)]

    def get_no_content_available_widget(self) -> Static:
        return NoContentAvailable("You have no working account")

    @property
    def check_if_should_be_updated(self) -> bool:
        working_account = (
            self.app.world.profile_data.working_account.name
            if _has_working_account(self.app.world.profile_data)
            else None
        )
        return working_account != self._previous_working_account

    @property
    def is_anything_to_display(self) -> bool:
        return _has_working_account(self.app.world.profile_data)

    @property
    def object_to_watch(self) -> TextualWorld:
        return self.app.world


class WorkingAccountChange(Vertical, CliveWidget):
    """Container used to change/set a new working account."""

    def __init__(self) -> None:
        super().__init__()
        self._working_account_input = AccountNameInput(required=False)

    def compose(self) -> ComposeResult:
        yield SectionTitle(
            "Change working account" if _has_working_account(self.app.world.profile_data) else "Set working account"
        )
        with Horizontal(id="input-with-button"):
            yield self._working_account_input
            yield CliveButton(
                "Change" if _has_working_account(self.app.world.profile_data) else "Set",
                variant="success",
                id_="change-working-account-button",
            )

    @on(CliveButton.Pressed, "#change-working-account-button")
    async def change_working_account(self) -> None:
        if not self._working_account_input.validate_passed():
            return

        account_name = self._working_account_input.value_or_error
        wrapper = await self.app.world.commands.does_account_exists_in_node(account_name=account_name)
        if wrapper.error_occurred:
            self.notify(f"Failed to check if account {account_name} exists in the node.", severity="warning")
            return

        if not wrapper.result_or_raise:
            self.notify(f"Account {account_name} does not exist in the node.", severity="warning")
            return

        self.app.world.profile_data.unset_working_account()
        self.app.world.profile_data.set_working_account(self._working_account_input.value_or_error)
        self.app.trigger_profile_data_watchers()
        self._working_account_input.input.clear()

    def change_container_function(self) -> None:
        button = CliveButton(
            "Change" if _has_working_account(self.app.world.profile_data) else "Set",
            variant="success",
            id_="change-working-account-button",
        )
        self.query_one(SectionTitle).update(
            "Change working account" if _has_working_account(self.app.world.profile_data) else "Set working account"
        )
        self.query_one(CliveButton).remove()
        self.query_one("#input-with-button").mount(button)


class WorkingAccount(TabPane, CliveWidget):
    """TabPane used to add and delete working account."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: str):
        super().__init__(title=title)
        self._previous_working_account = self.working_account

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield WorkingAccountChange()
            yield ManageWorkingAccountTable()

    def on_mount(self) -> None:
        self.watch(self.app.world, "profile_data", self._working_account_changed)

    def _working_account_changed(self) -> None:
        if self.working_account == self._previous_working_account:
            return
        self._previous_working_account = self.working_account
        self.query_one(WorkingAccountChange).change_container_function()

    @property
    def working_account(self) -> WorkingAccountType | None:
        if not self.app.world.profile_data.is_working_account_set():
            return None
        return self.app.world.profile_data.working_account

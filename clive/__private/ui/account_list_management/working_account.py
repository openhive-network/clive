from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal, Vertical
from textual.widgets import Label, Static, TabPane

from clive.__private.core.commands.find_accounts import AccountNotFoundError
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
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInputError
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section_title import SectionTitle
from clive.exceptions import FormValidationError

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.profile_data import ProfileData
    from clive.__private.core.world import TextualWorld
    from clive.__private.storage.accounts import Account


class RemoveWorkingAccountHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Label("Working account", classes=ODD_CLASS_NAME)
        yield Label("Action", classes=EVEN_CLASS_NAME)


class RemoveWorkingAccountRow(CliveCheckerboardTableRow, CliveWidget):
    def __init__(self, working_account: Account):
        super().__init__(
            CliveCheckerBoardTableCell(working_account.name),
            CliveCheckerBoardTableCell(CliveButton("Remove", variant="error", id_="remove-working-account-button")),
        )

    @on(CliveButton.Pressed, "#remove-working-account-button")
    def remove_working_account(self) -> None:
        self.app.world.profile_data.unset_working_account()
        self.app.world.profile_data.watched_accounts.clear()


class RemoveWorkingAccount(CliveCheckerboardTable):
    def __init__(self) -> None:
        super().__init__(
            Static("Remove working account", id="remove-working-account-title"),
            RemoveWorkingAccountHeader(),
            dynamic=True,
            attr_to_watch="profile_data",
        )
        self._previous_working_account: str | None = None

    def create_dynamic_rows(self, content: ProfileData) -> list[RemoveWorkingAccountRow]:
        self._previous_working_account = content.working_account.name if self._has_working_account else None

        return [RemoveWorkingAccountRow(self.app.world.profile_data.working_account)]

    def get_no_content_available_widget(self) -> Static:
        return Static("You have no working account", id="no-working-account-info")

    @property
    def check_if_should_be_updated(self) -> bool:
        working_account = self.app.world.profile_data.working_account.name if self._has_working_account else None
        return working_account != self._previous_working_account

    @property
    def is_anything_to_display(self) -> bool:
        return self._has_working_account

    @property
    def object_to_watch(self) -> TextualWorld:
        return self.app.world

    @property
    def _has_working_account(self) -> bool:
        return self.app.world.profile_data.is_working_account_set()


class WorkingAccountChange(Vertical, CliveWidget):
    def __init__(self) -> None:
        super().__init__()
        self._working_account_input = AccountNameInput()

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield SectionTitle("Change working account" if self._has_working_account else "Set working account")
            with Horizontal(id="input-with-button"):
                yield self._working_account_input
                yield CliveButton(
                    "change" if self._has_working_account else "set",
                    variant="success",
                    id_="change-working-account-button",
                )
        yield RemoveWorkingAccount()

    @on(CliveButton.Pressed, "#change-working-account-button")
    async def change_working_account(self) -> None:
        await self._check_is_account_appropriate()

        self.app.world.profile_data.unset_working_account()
        self.app.world.profile_data.set_working_account(self._working_account_input.value_or_error)
        self.app.world.profile_data.watched_accounts.clear()

    @property
    def _has_working_account(self) -> bool:
        return self.app.world.profile_data.is_working_account_set()

    async def _check_is_account_appropriate(self) -> None:
        try:
            account_name = self._working_account_input.value_or_error
        except CliveValidatedInputError as error:
            raise FormValidationError(str(error)) from error

        if not await self._does_account_exist_in_node(account_name):
            raise FormValidationError(f"Account {account_name} does not exist in the node.")

    async def _does_account_exist_in_node(self, account_name: str) -> bool:
        try:
            wrapper = await self.app.world.commands.find_accounts(accounts=[account_name])
        except AccountNotFoundError:
            return False
        else:
            return wrapper.success


class WorkingAccount(TabPane, CliveWidget):
    """TabPane used to add and delete working account."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def compose(self) -> ComposeResult:
        yield WorkingAccountChange()

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.widgets import Static

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.widgets.buttons import OneLineButton
from clive.__private.ui.widgets.buttons.cancel_button import CancelOneLineButton
from clive.__private.ui.widgets.buttons.confirm_button import ConfirmOneLineButton
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.authority.entries import AuthorityEntryAccountRegular, AuthorityEntryKeyRegular
    from clive.__private.core.authority.roles import AuthorityRoleRegular


class RestoreOrRemoveEntryDialog(CliveActionDialog[bool | None]):
    """
    Dialog for already edited entries - choose to restore original value or remove entry completely.

    Returns True as result when user chooses to restore entry, False when user chooses to remove entry,
    and None when cancelled.

    Attributes:
        DEFAULT_CSS: CSS styles specific to this dialog.
        RESTORE_OR_REMOVE_ENTRY_TEXT: Question displayed in main section of dialog.

    Args:
        role: Role that will be edited.
        current_entry: Entry that will is about to be removed or restored.
        initial_value: Initial value of current entry.
        initial_weight: Initial weight of current entry.
    """

    DEFAULT_CSS = """
    RestoreOrRemoveEntryDialog {
        CliveDialogContent {
            width: 50%;
            Static {
                text-align: center;
            }
        }
    }
    """

    RESTORE_OR_REMOVE_ENTRY_TEXT: Final[str] = (
        "Do you want to restore value of entry to its original state or remove the it completely?"
    )

    def __init__(
        self,
        role: AuthorityRoleRegular,
        current_entry: AuthorityEntryKeyRegular | AuthorityEntryAccountRegular,
    ) -> None:
        super().__init__("Restore or remove entry")
        self._role = role
        self._current_entry = current_entry

    def create_dialog_content(self) -> ComposeResult:
        with Section():
            yield Static(self.RESTORE_OR_REMOVE_ENTRY_TEXT)

    def create_buttons_content(self) -> ComposeResult:
        yield ConfirmOneLineButton("Restore entry")
        yield OneLineButton("Remove entry", id_="remove-entry-button", variant="error")
        yield CancelOneLineButton()

    async def _perform_confirmation(self) -> bool:
        from clive.__private.logger import logger

        value_to_replace = self._current_entry.value
        initial_value = self._current_entry.initial_value
        initial_weight = self._current_entry.weight
        logger.debug(f"ENTRY ID WHILE RESTORING{id(self._current_entry)}")
        self._current_entry.restore()
        self._role.replace(value_to_replace, initial_weight, initial_value)
        return True

    def _perform_removal(self) -> None:
        entry_current_value = self._current_entry.value
        self._role.remove(entry_current_value)
        assert not self._role.has(entry_current_value), (
            f"Entry {entry_current_value} was not removed from {self._role.level} role."
        )

    def _close_when_cancelled(self) -> None:
        self.dismiss()

    def _close_when_confirmed(self) -> None:
        """Used when user chooses to restore entry."""
        self.dismiss(result=True)

    def _close_when_removed(self) -> None:
        """Used when removal of original entry succeeded."""
        self.dismiss(result=False)

    @on(OneLineButton.Pressed, "#remove-entry-button")
    def _remove_with_button(self) -> None:
        self._perform_removal()
        self._close_when_removed()

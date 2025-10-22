from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.authority.entries import AuthorityEntryMemo
from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.widgets.inputs.authority_entry_memo_input import AuthorityEntryMemoInput
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.authority import AuthorityRoleMemo


class EditMemoEntryDialog(CliveActionDialog[AuthorityEntryMemo | None]):
    """
    Dialog for editing memo authority entry type.

    Attributes:
        DEFAULT_CSS: CSS styles specific to this dialog.

    Args:
        role: Role that will be edited.
    """

    DEFAULT_CSS = """
    EditMemoEntryDialog {
        CliveDialogContent {
            width: 85%;
        }

        AuthorityEntryMemoInput {
            margin-bottom: 1;
        }

        SelectCopyPasteHint {
            margin: 1 1 0 1;
        }
    }
    """

    def __init__(self, role: AuthorityRoleMemo) -> None:
        super().__init__(border_title=f"Edit {role.level_display} role entry")
        self._role = role

    @property
    def authority_entry_memo_input(self) -> AuthorityEntryMemoInput:
        return self.query_exactly_one(AuthorityEntryMemoInput)

    def create_dialog_content(self) -> ComposeResult:
        yield AuthorityEntryMemoInput(value=self._role.entry.value)
        yield SelectCopyPasteHint()

    async def _perform_confirmation(self) -> bool:
        authority_entry_memo_input = self.authority_entry_memo_input

        if not authority_entry_memo_input.validate_passed():
            return False

        authority_entry_memo_input_value = authority_entry_memo_input.value_or_error

        if self._role.entry.value == authority_entry_memo_input_value:
            self.notify("New memo key has the same value as previous one.", severity="error")
            return False

        self._role.set(authority_entry_memo_input_value)
        assert self._role.entry.value == authority_entry_memo_input_value, "Memo was not modified."

        return True

    def _close_when_cancelled(self) -> None:
        self.dismiss()

    def _close_when_confirmed(self) -> None:
        self.dismiss(result=self._role.entry)

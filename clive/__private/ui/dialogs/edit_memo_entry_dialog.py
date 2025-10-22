from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.authority.entries import AuthorityEntryMemo
from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.widgets.inputs.authority_entry_input import AuthorityEntryInput
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint
from clive.__private.validators.public_key_validator import PublicKeyValidator

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
        entry_current_value: Current value of the entry that will be edited.
    """

    DEFAULT_CSS = """
    EditMemoEntryDialog {
        CliveDialogContent {
            width: 85%;
        }

        AuthorityEntryInput {
            margin-bottom: 1;
        }

        SelectCopyPasteHint {
            margin: 1 1 0 1;
        }
    }
    """

    def __init__(self, role: AuthorityRoleMemo, entry_current_value: str) -> None:
        super().__init__(border_title=f"Edit {role.level_display} role entry")
        self._role = role
        self._entry_current_value = entry_current_value

    @property
    def authority_entry_input(self) -> AuthorityEntryInput:
        return self.query_exactly_one(AuthorityEntryInput)

    def create_dialog_content(self) -> ComposeResult:
        yield AuthorityEntryInput(
            title="Public key", value=self._entry_current_value, required=True, validators=PublicKeyValidator()
        )
        yield SelectCopyPasteHint()

    async def _perform_confirmation(self) -> bool:
        authority_entry_input = self.authority_entry_input
        authority_entry_input_value = authority_entry_input.value_raw

        if not authority_entry_input.validate_passed():
            self.notify("Public key value is not valid.", severity="error")
            return False

        if self._role.value == authority_entry_input_value:
            self.notify("New memo key has the same value as previous one.", severity="error")
            return False

        self._role.set(authority_entry_input_value)

        return True

    def _close_when_cancelled(self) -> None:
        self.dismiss()

    def _close_when_confirmed(self) -> None:
        authority_entry_input_value = self.authority_entry_input.value_raw
        new_entry = AuthorityEntryMemo(authority_entry_input_value)
        self.dismiss(result=new_entry)

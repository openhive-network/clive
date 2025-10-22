from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.authority.entries import (
    AuthorityEntryRegular,
)
from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.widgets.inputs.authority_weight_input import AuthorityWeightInput
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.authority import AuthorityRoleRegular


class EditAuthorityRegularEntryDialog(CliveActionDialog[AuthorityEntryRegular | None]):
    """
    Dialog for editing regular authority entry types.

    Attributes:
        DEFAULT_CSS: CSS styles specific to this dialog.

    Args:
        role: Role that will be edited.
        entry: Current value of the entry that will be edited.
    """

    DEFAULT_CSS = """
    EditAuthorityRegularEntryDialog {
        CliveDialogContent {
            width: 85%;
        }

        LabelizedInput {
            margin-bottom: 1;
        }
    }
    """

    def __init__(self, role: AuthorityRoleRegular, entry: str | AuthorityEntryRegular) -> None:
        super().__init__(border_title=f"Edit {role.level_display} role entry")
        self._role = role
        self._entry = role.get_entry(entry)

    @property
    def weight_input(self) -> AuthorityWeightInput:
        return self.query_exactly_one(AuthorityWeightInput)

    def create_dialog_content(self) -> ComposeResult:
        yield LabelizedInput("Account or public key", self._entry.value)
        yield AuthorityWeightInput(value=self._entry.weight)

    async def _perform_confirmation(self) -> bool:
        weight_input = self.weight_input

        if not weight_input.validate_passed():
            return False

        new_weight = weight_input.value_or_error
        entry_value = self._entry.value

        if self._role.has(entry_value, new_weight):
            self.notify(f"{self._role.level} role already has entry like this one.", severity="warning")
            return False

        self._role.replace(entry_value, new_weight)
        assert self._role.has(entry_value, new_weight), "Entry was not modified."

        return True

    def _close_when_cancelled(self) -> None:
        self.dismiss()

    def _close_when_confirmed(self) -> None:
        new_entry = self._role.get_entry(self._entry.value)
        self.dismiss(result=new_entry)

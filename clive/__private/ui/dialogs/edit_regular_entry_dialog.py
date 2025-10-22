from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.authority.entries import (
    AuthorityEntryAccountRegular,
    AuthorityEntryKeyRegular,
)
from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.widgets.inputs.authority_weight_input import AuthorityWeightInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.authority import AuthorityRoleRegular


class EditRegularEntryDialog(CliveActionDialog[AuthorityEntryAccountRegular | AuthorityEntryKeyRegular | None]):
    """
    Dialog for editing regular authority entry types.

    Attributes:
        DEFAULT_CSS: CSS styles specific to this dialog.

    Args:
        role: Role that will be edited.
        entry: Current value of the entry that will be edited.
    """

    DEFAULT_CSS = """
    EditRegularEntryDialog {
        CliveDialogContent {
            width: 85%;
        }

        LabelizedInput {
            margin-bottom: 1;
        }
    }
    """

    def __init__(
        self, role: AuthorityRoleRegular, entry: AuthorityEntryAccountRegular | AuthorityEntryKeyRegular
    ) -> None:
        super().__init__(border_title=f"Edit {role.level_display} role entry")
        self._role = role
        self._entry = entry

    @property
    def weight_input(self) -> IntegerInput:
        return self.query_exactly_one(IntegerInput)

    def create_dialog_content(self) -> ComposeResult:
        yield LabelizedInput("Account or public key", self._entry.value)
        yield AuthorityWeightInput(value=self._entry.weight)

    async def _perform_confirmation(self) -> bool:
        weight_input = self.weight_input

        if not weight_input.validate_passed():
            return False

        new_weight_value = weight_input.value_or_error

        if self._role.has(self._entry.value, new_weight_value):
            self.notify(f"{self._role.level} role already has entry like this one.", severity="error")
            return False

        self._role.replace(self._entry.value, new_weight_value)
        assert self._role.has(self._entry.value, new_weight_value), "Entry was not modified."

        return True

    def _close_when_cancelled(self) -> None:
        self.dismiss()

    def _close_when_confirmed(self) -> None:
        new_entry = self._role.get_entry(self._entry.value)
        self.dismiss(result=new_entry)

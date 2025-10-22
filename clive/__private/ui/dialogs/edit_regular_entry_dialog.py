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
        current_entry: Current value of the entry that will be edited.
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
        self, role: AuthorityRoleRegular, current_entry: AuthorityEntryAccountRegular | AuthorityEntryKeyRegular
    ) -> None:
        super().__init__(border_title=f"Edit {role.level_display} role entry")
        self._role = role
        self._current_entry = current_entry

    @property
    def entry_value_label(self) -> LabelizedInput:
        return self.query_exactly_one(LabelizedInput)

    @property
    def weight_input(self) -> IntegerInput:
        return self.query_exactly_one(IntegerInput)

    def create_dialog_content(self) -> ComposeResult:
        yield LabelizedInput("Account or public key", self._current_entry.value)
        yield AuthorityWeightInput(value=self._current_entry.weight)

    async def _perform_confirmation(self) -> bool:
        entry_value = self.entry_value_label.value_or_error

        weight_input = self.weight_input
        weight_input_value = weight_input.value_or_error

        if not weight_input.validate_passed():
            self.notify("Weight input value is not valid.", severity="error")
            return False

        if self._role.has(entry_value, weight_input_value):
            self.notify(f"{self._role.level} role already has entry like this one.", severity="error")
            return False

        self._role.replace(self._current_entry.value, weight_input_value)

        return True

    def _close_when_cancelled(self) -> None:
        self.dismiss()

    def _close_when_confirmed(self) -> None:
        entry_value = self.entry_value_label.value_or_error

        new_entry: AuthorityEntryAccountRegular | AuthorityEntryKeyRegular | None = None

        weight_input_value = self.weight_input.value_or_error
        previous_entry_value = self._current_entry.value
        previous_entry_weight = self._current_entry.weight
        if self._current_entry.is_account:
            new_entry = AuthorityEntryAccountRegular(
                entry_value, weight_input_value, previous_entry_value, previous_entry_weight
            )
        else:
            new_entry = AuthorityEntryKeyRegular(
                entry_value, weight_input_value, previous_entry_value, previous_entry_weight
            )

        self.dismiss(result=new_entry)

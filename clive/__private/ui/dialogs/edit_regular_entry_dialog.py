from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.accounts.exceptions import AccountNotFoundError
from clive.__private.core.authority.entries import (
    AuthorityEntryAccountRegular,
    AuthorityEntryKeyRegular,
)
from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.widgets.inputs.authority_entry_input import AuthorityEntryInput
from clive.__private.ui.widgets.inputs.authority_weight_input import AuthorityWeightInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint
from clive.__private.validators.authority_entry_validator import AuthorityEntryValidator

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

        AuthorityEntryInput {
            margin-bottom: 1;
        }

        SelectCopyPasteHint {
            margin: 1 1 0 1;
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
    def authority_entry_input(self) -> AuthorityEntryInput:
        return self.query_exactly_one(AuthorityEntryInput)

    @property
    def weight_input(self) -> IntegerInput:
        return self.query_exactly_one(IntegerInput)

    def create_dialog_content(self) -> ComposeResult:
        yield AuthorityEntryInput(value=self._current_entry.value, required=False, validators=AuthorityEntryValidator())
        yield AuthorityWeightInput(value=self._current_entry.weight)
        yield SelectCopyPasteHint()

    async def _perform_confirmation(self) -> bool:
        authority_entry_input = self.authority_entry_input
        authority_entry_input_value = authority_entry_input.value_raw

        weight_input = self.weight_input
        weight_input_value = int(weight_input.value_raw)

        if not weight_input.validate_passed() or not authority_entry_input.validate_passed():
            self.notify("Authority or weight input values are not valid.", severity="error")
            return False

        try:
            await self.authority_entry_input.validate_account_existence_in_node()
        except AccountNotFoundError:
            return False

        if self._role.has(authority_entry_input_value, weight_input_value):
            self.notify(f"{self._role.level} role already has entry like this one.", severity="error")
            return False

        self._role.replace(self._current_entry.value, weight_input_value, authority_entry_input_value)

        return True

    def _close_when_cancelled(self) -> None:
        self.dismiss()

    def _close_when_confirmed(self) -> None:
        authority_entry_input = self.authority_entry_input
        authority_entry_input_value = authority_entry_input.value_raw

        new_entry: AuthorityEntryAccountRegular | AuthorityEntryKeyRegular | None = None

        weight_input_value = int(self.weight_input.value_raw)
        if authority_entry_input.holds_account_name:
            new_entry = AuthorityEntryAccountRegular(authority_entry_input_value, weight_input_value)
        else:
            new_entry = AuthorityEntryKeyRegular(authority_entry_input_value, weight_input_value)

        self.dismiss(result=new_entry)

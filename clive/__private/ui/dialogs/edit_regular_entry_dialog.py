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
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint

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

        AuthorityEntryInput {
            margin-bottom: 1;
        }

        SelectCopyPasteHint {
            margin: 1 1 0 1;
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
    def entry_input(self) -> AuthorityEntryInput:
        return self.query_exactly_one(AuthorityEntryInput)

    @property
    def weight_input(self) -> IntegerInput:
        return self.query_exactly_one(IntegerInput)

    def create_dialog_content(self) -> ComposeResult:
        yield AuthorityEntryInput(value=self._entry.value)
        yield AuthorityWeightInput(value=self._entry.weight)
        yield SelectCopyPasteHint()

    async def _perform_confirmation(self) -> bool:
        entry_input = self.entry_input
        weight_input = self.weight_input

        if not CliveValidatedInput.validate_many(weight_input, entry_input, notify_on_validation_error=True):
            return False

        new_entry_value = entry_input.value_or_error
        new_weight_value = weight_input.value_or_error

        try:
            await self.entry_input.validate_account_existence_in_node()
        except AccountNotFoundError:
            return False

        if self._role.has(new_entry_value, new_weight_value):
            self.notify(f"{self._role.level} role already has entry like this one.", severity="error")
            return False

        self._role.replace(self._entry.value, new_weight_value, new_entry_value)
        return True

    def _close_when_cancelled(self) -> None:
        self.dismiss()

    def _close_when_confirmed(self) -> None:
        new_entry = self._role.get_entry(self.entry_input.value_or_error)
        self.dismiss(result=new_entry)

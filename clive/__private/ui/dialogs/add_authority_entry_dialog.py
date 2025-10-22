from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.authority.entries import AuthorityEntryAccountRegular, AuthorityEntryKeyRegular
from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.widgets.inputs.authority_entry_input import AuthorityEntryInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint
from clive.__private.validators.authority_weight_validator import AuthorityWeightValidator

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.authority import AuthorityRoleRegular


class AddAuthorityEntryDialog(CliveActionDialog[AuthorityEntryAccountRegular | AuthorityEntryKeyRegular | None]):
    DEFAULT_CSS = """
    AddAuthorityEntryDialog {
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

    def __init__(self, role: AuthorityRoleRegular) -> None:
        super().__init__(border_title=f"Add new {role.level_display} role entry")
        self._role = role

    @property
    def authority_entry_input(self) -> AuthorityEntryInput:
        return self.query_exactly_one(AuthorityEntryInput)

    @property
    def weight_input(self) -> IntegerInput:
        return self.query_exactly_one(IntegerInput)

    def create_dialog_content(self) -> ComposeResult:
        yield AuthorityEntryInput()
        yield IntegerInput("Weight", always_show_title=True, value=1, validators=[AuthorityWeightValidator()])
        yield SelectCopyPasteHint()

    async def _perform_confirmation(self) -> bool:
        authority_entry_input = self.authority_entry_input
        weight_input = self.weight_input

        if not authority_entry_input.validate_passed() or not weight_input.validate_passed():
            self.notify("Input values are not valid.", severity="error")
            return False

        authority_entry_input_value = authority_entry_input.value_raw
        weight_input_value = int(weight_input.value_raw)

        if not await self.authority_entry_input.validate_account_existence_in_node():
            return False

        if self._role.has(authority_entry_input_value):
            self.notify(f"{self._role.level} role already has this entry.", severity="error")
            return False

        self._role.add(authority_entry_input_value, weight_input_value)

        return True

    def _close_when_cancelled(self) -> None:
        self.dismiss()

    def _close_when_confirmed(self) -> None:
        authority_entry_input = self.authority_entry_input
        authority_entry_input_value = authority_entry_input.value_raw
        weight_input_value = int(self.weight_input.value_raw)
        new_entry: AuthorityEntryAccountRegular | AuthorityEntryKeyRegular | None = None

        if authority_entry_input.holds_account_name:
            new_entry = AuthorityEntryAccountRegular(authority_entry_input_value, weight_input_value)
        else:
            new_entry = AuthorityEntryKeyRegular(authority_entry_input_value, weight_input_value)
        self.dismiss(result=new_entry)

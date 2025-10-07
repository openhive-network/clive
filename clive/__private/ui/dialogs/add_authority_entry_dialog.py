from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.widgets.inputs.authority_entry_input import AuthorityEntryInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint
from clive.__private.core.authority.entries import AuthorityEntryAccountRegular, AuthorityEntryKeyRegular
from clive.__private.validators.authority_weight_validator import AuthorityWeightValidator

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from clive.__private.core.types import AuthorityLevel


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

    def __init__(self, role_level: AuthorityLevel) -> None:
        super().__init__(border_title=f"Add new {role_level} role entry")
        self._role_level = role_level

    @property
    def authority_entry_input(self) -> AuthorityEntryInput:
        return self.query_exactly_one(AuthorityEntryInput)
    
    @property
    def weight_input(self) -> IntegerInput:
        return self.query_exactly_one(IntegerInput)

    def create_dialog_content(self) -> ComposeResult:
        yield AuthorityEntryInput()
        yield IntegerInput("Weight",
            always_show_title=True,
            value=1,
            validators=[AuthorityWeightValidator()])
        yield SelectCopyPasteHint()

    async def _perform_confirmation(self) -> bool:
        authority_entry_input = self.authority_entry_input.input
        weight_input = self.weight_input.input

        if not authority_entry_input.is_valid or not weight_input.is_valid:
            self.notify(f"Input values are not valid.", severity="error")
            return False
        
        authority_entry_input_value = authority_entry_input.value
        weight_input_value = int(weight_input.value)

        if self.authority_entry_input.holds_account_name:
            account_name = authority_entry_input_value
            wrapper = await self.commands.does_account_exists_in_node(account_name=account_name)
            if wrapper.error_occurred:
                self.notify(f"Failed to check if account {account_name} exists in the node.")
                return False

            if not wrapper.result_or_raise:
                self.notify("Account not found in the node.", severity="error")
                return False
            
        current_role = self.profile.accounts.working.data.authority.get_role_by_level(self._role_level)
        if current_role.has(authority_entry_input_value, weight_input_value):
            self.notify(f"{current_role.level} role already has this entry.")
            return False
        
        current_role.add(authority_entry_input_value, weight_input_value)

        return True
        
    def _close_when_confirmed(self) -> None:
        authority_entry_input = self.authority_entry_input
        authority_entry_input_value = authority_entry_input.input.value
        weight_input_value = int(self.weight_input.input.value)
        new_entry: AuthorityEntryAccountRegular | AuthorityEntryKeyRegular | None = None


        if authority_entry_input.holds_account_name:
            new_entry = AuthorityEntryAccountRegular(authority_entry_input_value, weight_input_value)
        else:
            new_entry = AuthorityEntryKeyRegular(authority_entry_input_value, weight_input_value)
        self.dismiss(result=new_entry)

    def _close_when_cancelled(self) -> None:
        self.dismiss()

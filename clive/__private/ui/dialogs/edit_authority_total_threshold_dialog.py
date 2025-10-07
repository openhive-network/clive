from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.authority.roles import AuthorityRoleRegular
from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.widgets.inputs.authority_entry_input import AuthorityEntryInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint
from clive.__private.core.authority.entries import AuthorityEntryAccountRegular, AuthorityEntryKeyRegular
from clive.__private.validators.authority_weight_validator import AuthorityWeightValidator

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from clive.__private.core.types import AuthorityLevel


class EditAuthorityTotalThresholdDialog(CliveActionDialog[int]):
    DEFAULT_CSS = """
    AddAuthorityEntryDialog {
        CliveDialogContent {
            width: 85%;
        }
    }
    """

    def __init__(self, role_level: AuthorityLevel) -> None:
        super().__init__(border_title=f"Edit {role_level} role weight threshold")
        self._role_level = role_level

    @property
    def current_role(self) -> AuthorityRoleRegular:
        return self.profile.accounts.working.data.authority.get_role_by_level(self._role_level)
    
    @property
    def weight_input(self) -> IntegerInput:
        return self.query_exactly_one(IntegerInput)

    def create_dialog_content(self) -> ComposeResult:
        from clive.__private.logger import logger
        logger.debug(f"CURRENT ROLE {self.current_role}")
        yield IntegerInput("Weight",
            always_show_title=True,
            value=self.current_role.weight_threshold,
            validators=[AuthorityWeightValidator()])

    async def _perform_confirmation(self) -> bool:
        weight_input = self.weight_input.input

        if not weight_input.is_valid:
            self.notify(f"Value of weight is not valid.", severity="error")
            return False
        current_role = self.current_role
        weight_input_value = int(weight_input.value)
        if weight_input_value == current_role.weight_threshold:
            self.notify("New weight has the same value as previous one.", severity="error")
            return False
        current_role.set_threshold(weight_input_value)
        
        return True
        
    def _close_when_confirmed(self) -> None:
        self.dismiss(result=int(self.weight_input.input.value))

    def _close_when_cancelled(self) -> None:
        self.dismiss()

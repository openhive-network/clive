from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.widgets.inputs.authority_weight_input import AuthorityWeightInput

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.authority import AuthorityRoleRegular


class EditAuthorityTotalThresholdDialog(CliveActionDialog[int]):
    """
    Dialog for editing total threshold of role.

    Attributes:
        DEFAULT_CSS: CSS styles specific to this dialog.

    Args:
        role: Role that threshold will be modified.
    """

    DEFAULT_CSS = """
    EditAuthorityTotalThresholdDialog {
        CliveDialogContent {
            width: 35%;
        }
    }
    """

    def __init__(self, role: AuthorityRoleRegular) -> None:
        super().__init__(border_title=f"Edit {role.level_display} role weight threshold")
        self._role = role

    @property
    def weight_input(self) -> AuthorityWeightInput:
        return self.query_exactly_one(AuthorityWeightInput)

    def create_dialog_content(self) -> ComposeResult:
        yield AuthorityWeightInput(value=self._role.weight_threshold)

    async def _perform_confirmation(self) -> bool:
        weight_input = self.weight_input

        if not weight_input.validate_passed():
            return False

        new_weight = weight_input.value_or_error

        role = self._role
        if new_weight == role.weight_threshold:
            self.notify("New weight has the same value as previous one.", severity="warning")
            return False

        role.set_threshold(new_weight)
        assert role.weight_threshold == new_weight, "Failed to assign new value to weight threshold."

        return True

    def _close_when_cancelled(self) -> None:
        self.dismiss()

    def _close_when_confirmed(self) -> None:
        self.dismiss(result=self._role.weight_threshold)

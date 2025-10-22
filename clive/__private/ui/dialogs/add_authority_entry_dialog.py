from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.authority.entries import AuthorityEntryRegular
from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.widgets.inputs.authority_entry_regular_input import AuthorityEntryRegularInput
from clive.__private.ui.widgets.inputs.authority_weight_input import AuthorityWeightInput
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.authority import AuthorityRoleRegular


class AddAuthorityEntryDialog(CliveActionDialog[AuthorityEntryRegular | None]):
    """
    Dialog for adding new entries.

    Attributes:
        DEFAULT_CSS: CSS styles specific to this dialog.

    Args:
        role: Role that will get new entry.
    """

    DEFAULT_CSS = """
    AddAuthorityEntryDialog {
        CliveDialogContent {
            width: 85%;
        }

        AuthorityEntryRegularInput {
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
    def authority_entry_input(self) -> AuthorityEntryRegularInput:
        return self.query_exactly_one(AuthorityEntryRegularInput)

    @property
    def weight_input(self) -> AuthorityWeightInput:
        return self.query_exactly_one(AuthorityWeightInput)

    def create_dialog_content(self) -> ComposeResult:
        yield AuthorityEntryRegularInput()
        yield AuthorityWeightInput()
        yield SelectCopyPasteHint()

    async def _perform_confirmation(self) -> bool:
        authority_entry_input = self.authority_entry_input
        weight_input = self.weight_input

        if not CliveValidatedInput.validate_many(authority_entry_input, weight_input):
            return False

        new_entry = authority_entry_input.value_or_error
        new_weight = weight_input.value_or_error

        if authority_entry_input.holds_account_name and not await self.app.does_account_exist_in_node(new_entry):
            return False

        if self._role.has(new_entry):
            self.notify(f"{self._role.level} role already has this entry.", severity="warning")
            return False

        self._role.add(new_entry, new_weight)

        assert self._role.has(new_entry, new_weight), f"New entry was not added to {self._role.level_display} role."

        return True

    def _close_when_cancelled(self) -> None:
        self.dismiss()

    def _close_when_confirmed(self) -> None:
        authority_entry_input_value = self.authority_entry_input.value_or_error
        new_entry = self._role.get_entry(authority_entry_input_value)
        self.dismiss(result=new_entry)

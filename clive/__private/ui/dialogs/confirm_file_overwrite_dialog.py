from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.dialogs.confirm_action_dialog import ConfirmActionDialog

if TYPE_CHECKING:
    from typing import Final


class ConfirmFileOverwriteDialog(ConfirmActionDialog):
    """Dialog to confirm if the user wants to save to existing file."""

    CONFIRM_QUESTION_SAVE_TO_EXISTING_FILE: Final[str] = "The file already exists. Do you want to overwrite it?"

    def __init__(self) -> None:
        super().__init__(confirm_question=self.CONFIRM_QUESTION_SAVE_TO_EXISTING_FILE)

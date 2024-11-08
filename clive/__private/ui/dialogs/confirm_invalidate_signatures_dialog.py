from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.dialogs.confirm_action_dialog import ConfirmActionDialog

if TYPE_CHECKING:
    from typing import Final


class ConfirmInvalidateSignaturesDialog(ConfirmActionDialog):
    """Dialog to confirm if the user wants to invalidate signatures of loaded transaction."""

    CONFIRM_QUESTION_REFRESH_METADATA: Final[str] = (
        "Transaction loaded from file contains signatures.\n"
        "Confirming this action will invalidate them.\n\n"
        "Are you sure you want to proceed?"
    )

    def __init__(self) -> None:
        super().__init__(confirm_question=self.CONFIRM_QUESTION_REFRESH_METADATA)

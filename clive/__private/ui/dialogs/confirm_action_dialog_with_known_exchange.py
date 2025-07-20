from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.dialogs.confirm_action_dialog import ConfirmActionDialog

if TYPE_CHECKING:
    from typing import Final


class ConfirmActionDialogWithKnownExchange(ConfirmActionDialog):
    """
    Dialog to confirm if the user wants to proceed operation with a known exchange.

    Attributes:
        CONFIRM_QUESTION_KNOWN_EXCHANGE_IN_INPUT: The question to confirm the operation with a known exchange.
    """

    CONFIRM_QUESTION_KNOWN_EXCHANGE_IN_INPUT: Final[str] = (
        "Recipient of your operation is a known exchange.\n"
        "Exchanges usually don't support this operation.\n\n"
        "Are you sure you want to proceed?"
    )

    def __init__(self) -> None:
        super().__init__(confirm_question=self.CONFIRM_QUESTION_KNOWN_EXCHANGE_IN_INPUT)

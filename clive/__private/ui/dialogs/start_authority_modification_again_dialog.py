from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.dialogs.confirm_action_dialog import ConfirmActionDialog

if TYPE_CHECKING:
    from clive.__private.models.schemas import AccountName


class StartAuthorityModificationAgainDialog(ConfirmActionDialog):
    """
    Dialog to confirm whether the user wants to start modifying authority from scratch.

    Args:
        account_name: Name of the account whose authority was already modified by the operation placed in cart.
    """

    def __init__(self, account_name: AccountName) -> None:
        confirm_question = (
            f"Operation that modifies authority of {account_name} account "
            "is already added to cart. Do you want to remove existing one and start over?"
        )
        super().__init__(confirm_question=confirm_question)

from __future__ import annotations

from typing import Final

from clive.__private.ui.styling import colorize_shortcut

PRESS_HELP_MESSAGE: Final[str] = (
    f"In any moment you can press the {colorize_shortcut('F1')} button to see the Help page."
)

BAD_ACCOUNT_IN_LOADED_TRANSACTION_MESSAGE: Final[str] = (
    "The transaction contains an operation to a bad account that is not present in the list of known accounts."
)

ERROR_BAD_ACCOUNT_IN_LOADED_TRANSACTION_MESSAGE: Final[str] = (
    f"You cannot load the transaction from a file.\n{BAD_ACCOUNT_IN_LOADED_TRANSACTION_MESSAGE}"
)

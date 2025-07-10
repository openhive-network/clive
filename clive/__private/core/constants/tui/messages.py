from __future__ import annotations

from typing import Final

from clive.__private.ui.styling import colorize_shortcut

BAD_ACCOUNT_IN_LOADED_TRANSACTION_MESSAGE: Final[str] = (
    "The transaction contains an operation to a bad account that is not present in the list of known accounts."
)

ERROR_BAD_ACCOUNT_IN_LOADED_TRANSACTION_MESSAGE: Final[str] = (
    f"You cannot load the transaction from a file.\n{BAD_ACCOUNT_IN_LOADED_TRANSACTION_MESSAGE}"
)


def get_press_help_message(shortcut: str) -> str:
    return f"In any moment you can press {colorize_shortcut(shortcut)} to see the Help page."

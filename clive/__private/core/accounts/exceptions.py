from __future__ import annotations

from clive.exceptions import CliveError


class AccountAccessError(CliveError):
    """Base class for errors related with account accessibility."""


class NoWorkingAccountError(AccountAccessError):
    """No working account is available."""

    def __int__(self) -> None:
        super().__init__("Working account is not available. Set working account first.")


class AccountNotFoundError(AccountAccessError):
    """Raised when an account is not found."""

    def __init__(self, account_name: str) -> None:
        super().__init__(f"Account {account_name} not found.")
        self.account_name = account_name

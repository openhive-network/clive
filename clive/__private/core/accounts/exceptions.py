from __future__ import annotations

from clive.exceptions import CliveError


class AccountAccessError(CliveError):
    """Base class for errors related with account accessibility."""


class AccountsUpdateError(CliveError):
    """Base class for errors related with accounts update."""


class NoWorkingAccountError(AccountAccessError):
    """No working account is available."""

    def __int__(self) -> None:
        """
        Initialize the NoWorkingAccountError with a message.

        Returns:
            None
        """
        super().__init__("Working account is not available. Set working account first.")


class AccountNotFoundError(AccountAccessError):
    """Raised when an account is not found."""

    def __init__(self, account_name: str) -> None:
        """
        Initialize the AccountNotFoundError with the account name.

        Args:
            account_name: The name of the account that was not found.

        Returns:
            None
        """
        super().__init__(f"Account {account_name} not found.")
        self.account_name = account_name


class AccountAlreadyExistsError(AccountsUpdateError):
    """Raised when account already exists in some place."""

    def __init__(self, account_name: str, place: str) -> None:
        """
        Initialize the AccountAlreadyExistsError with the account name and place.

        Args:
            account_name: The name of the account that already exists.
            place: The place where the account already exists (e.g., "tracked accounts", "watched accounts").

        Returns:
            None
        """
        super().__init__(f"Account {account_name} already exists in {place}.")
        self.account_name = account_name
        self.place = place


class TryingToAddBadAccountError(AccountsUpdateError):
    """Raised when trying to add a bad account to tracked accounts."""

    def __init__(self, account_name: str) -> None:
        """
        Initialize the TryingToAddBadAccountError with the account name.

        Args:
            account_name: The name of the account that is being added.

        Returns:
            None
        """
        super().__init__(f"Trying to add a bad account {account_name} to tracked accounts.")

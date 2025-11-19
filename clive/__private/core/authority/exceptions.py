from __future__ import annotations

from clive.exceptions import CliveError


class AuthorityError(CliveError):
    """Base class for errors related with account authority."""


class AuthorityEntryNotFoundError(AuthorityError):
    """
    Raised when an authority entry is not found.

    Args:
        entry_value: Value of entry that was not found.
    """

    def __init__(self, entry_value: str) -> None:
        super().__init__(f"Authority entry with value with value {entry_value} not found.")

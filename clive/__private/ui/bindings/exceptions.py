"""Exceptions for the bindings system."""

from __future__ import annotations

from clive.exceptions import CliveError


class BindingsDeserializeError(CliveError):
    """Error during binding deserialization.

    Raised when the bindings dictionary is loaded from TOML but cannot be used to create a CliveBindings.
    This might be due to incorrect TOML sections or fields, missing required bindings,
    or other structural issues in the binding configuration.
    """


class BindingFileInvalidError(CliveError):
    """Raise when file with bindings loaded has invalid format."""

    def __init__(self, message: str) -> None:
        super().__init__(message)

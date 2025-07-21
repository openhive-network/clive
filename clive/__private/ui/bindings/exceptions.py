from __future__ import annotations

from clive.exceptions import CliveError


class BindingFileInvalidError(CliveError):
    """Raised when loaded file with bindings has invalid format.

    Args:
        message: Short description of a problem, message will be displayed as part of notification to user.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class BindingsDeserializeError(CliveError):
    """
    Raised when the bindings dictionary is loaded from TOML but cannot be used to create a CliveBindings.

    This might be due to incorrect TOML sections or fields.
    """

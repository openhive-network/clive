from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import Response


class CliveError(Exception):
    """Base class for all clive exceptions."""


class CommunicationError(CliveError):
    """Base class for all communication exceptions."""


class UnknownResponseFormatError(CommunicationError):
    """Raised when the response format is unknown."""

    def __init__(self, response: Response) -> None:
        self.response = response
        message = (
            f"Unknown response format from url={response.url}\n"
            f"data={response.request.content!r}, result={response.json()}"
        )
        super().__init__(message)


class NoItemSelectedError(CliveError):
    """Raised when tried to access `selected` property of Select widget when no item was selected."""


class ScreenError(CliveError):
    """Base class for all screen exceptions."""


class ScreenNotFoundError(ScreenError):
    """Raised when screen is not found."""


class FormValidationError(CliveError):
    def __init__(self, reason: str, *, given_value: str | None = None) -> None:
        self.reason = reason
        self.given_value = given_value
        super().__init__()


class NodeAddressError(FormValidationError):
    """Base class for all node address exceptions."""


class PrivateKeyInvalidFormatFormError(FormValidationError):
    def __init__(self, given_key: str | None = None) -> None:
        super().__init__(f"Given key is in invalid form: `{given_key}`", given_value=given_key)


class InputTooShortError(FormValidationError):
    def __init__(self, *, expected_length: int, given_value: str) -> None:
        super().__init__(
            f"Expected length of {expected_length}, but string of {len(given_value)} given", given_value=given_value
        )


class RepeatedPasswordIsDifferentError(FormValidationError):
    def __init__(self) -> None:
        super().__init__("Repeated password is different than original one")


class AliasAlreadyInUseError(FormValidationError):
    def __init__(self, alias: str) -> None:
        super().__init__(f"Alias `{alias}` is already in use.", given_value=alias)


class PrivateKeyAlreadyInUseError(FormValidationError):
    def __init__(self) -> None:
        super().__init__("Private key is already in use.")


class CannotActivateError(CliveError):
    pass


class TransactionNotSignedError(CliveError):
    pass

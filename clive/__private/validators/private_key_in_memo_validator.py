from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Validator

from clive.__private.validators.private_key_validation_tools import contains_private_key

if TYPE_CHECKING:
    from textual.validation import ValidationResult

    from clive.__private.core.world import World


class PrivateKeyInMemoValidator(Validator):
    """
    Validator that checks if memo content contains private keys for tracked accounts.

    Prevents accidental exposure of private keys by scanning memo text
    against all tracked account authorities (owner, active, posting, memo).

    Attributes:
        PRIVATE_KEY_IN_MEMO_FAILURE_DESCRIPTION: Error message returned when a private key is detected in memo.

    Args:
        world: The world object providing access to tracked accounts and wax interface.
    """

    PRIVATE_KEY_IN_MEMO_FAILURE_DESCRIPTION: Final[str] = "Private key detected"

    def __init__(self, world: World) -> None:
        super().__init__()
        self._world = world

    def validate(self, value: str) -> ValidationResult:
        if contains_private_key(value, self._world):
            return self.failure(self.PRIVATE_KEY_IN_MEMO_FAILURE_DESCRIPTION, value)
        return self.success()

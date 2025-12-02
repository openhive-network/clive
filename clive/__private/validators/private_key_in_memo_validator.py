from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Validator

from clive.__private.validators.private_key_validation_tools import contains_private_key

if TYPE_CHECKING:
    from textual.validation import ValidationResult

    from clive.__private.core.world import World


class PrivateKeyInMemoValidator(Validator):
    PRIVATE_KEY_IN_MEMO_FAILURE_DESCRIPTION: Final[str] = "Private key detected"

    def __init__(self, world: World) -> None:
        super().__init__()
        self._world = world

    def validate(self, memo_value: str) -> ValidationResult:
        if contains_private_key(memo_value, self._world):
            return self.failure(self.PRIVATE_KEY_IN_MEMO_FAILURE_DESCRIPTION, memo_value)
        return self.success()

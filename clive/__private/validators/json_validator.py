from __future__ import annotations

import json
from typing import TYPE_CHECKING, Final

from textual.validation import Validator

if TYPE_CHECKING:
    from textual.validation import ValidationResult


class JsonValidator(Validator):
    INVALID_JSON_DESCRIPTION: Final[str] = "The input is not a valid JSON"

    def validate(self, value: str) -> ValidationResult:
        if self._is_valid_json(value):
            return self.success()

        return self.failure(self.INVALID_JSON_DESCRIPTION, value)

    def _is_valid_json(self, value: str) -> bool:
        try:
            json.loads(value)
        except json.JSONDecodeError:
            return False
        return True

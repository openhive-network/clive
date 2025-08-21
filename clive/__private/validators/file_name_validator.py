from __future__ import annotations

from typing import Final

from textual.validation import Function, ValidationResult, Validator

from clive.__private.validators.filesystem_validation_tools import (
    validate_filename,
)


class FileNameValidator(Validator):
    NOT_A_PROPER_FILE_NAME_DESC: Final[str] = "File name is not valid."

    def validate(self, value: str) -> ValidationResult:
        return Function(validate_filename, self.NOT_A_PROPER_FILE_NAME_DESC).validate(value)

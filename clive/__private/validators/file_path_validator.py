from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal

from textual.validation import Function, ValidationResult, Validator

from clive.__private.validators.file_name_validator import FileNameValidator
from clive.__private.validators.filesystem_validation_tools import (
    validate_is_file_or_can_be_file,
    validate_path_is_file,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


class FilePathValidator(Validator):
    NOT_A_FILE_FAILURE_DESC: Final[str] = "Path should be a file"
    NOT_A_FILE_OR_CANT_BE_FILE_FAILURE_DESC: Final[str] = "Path is not a file or can't be a file."

    type Modes = Literal[
        "is_file",
        "is_file_or_can_be_file",
    ]

    def __init__(self, mode: Modes, root_directory_path: Path) -> None:
        super().__init__()
        self.mode = mode
        self._root_directory_path = root_directory_path

    def update_root_directory_path(self, root_path: Path) -> None:
        self._root_directory_path = root_path

    def validate(self, value: str) -> ValidationResult:
        validate_filename_result = FileNameValidator().validate(value)

        mode_validators: dict[FilePathValidator.Modes, tuple[Callable[[str], bool], str]] = {
            "is_file": (validate_path_is_file, self.NOT_A_FILE_FAILURE_DESC),
            "is_file_or_can_be_file": (
                validate_is_file_or_can_be_file,
                self.NOT_A_FILE_OR_CANT_BE_FILE_FAILURE_DESC,
            ),
        }

        method = mode_validators[self.mode][0]
        desc = mode_validators[self.mode][1]
        mode_validator = Function(method, desc)

        validation_results = [validate_filename_result, mode_validator.validate(str(self._get_filepath(value)))]
        return ValidationResult.merge(validation_results)

    def _get_filepath(self, value: str) -> Path:
        return self._root_directory_path / value

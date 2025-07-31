from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal

from textual.validation import Function, ValidationResult, Validator

from clive.__private.validators.filesystem_validation_tools import (
    validate_filename,
    validate_is_file_or_can_be_file,
    validate_path_is_file,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class FilePathValidator(Validator):
    INVALID_PATH_FAILURE_DESC: Final[str] = "Path is invalid (couldn't resolve)."
    NOT_A_PROPER_FILE_NAME: Final[str] = "File name is not valid."
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

    def update_root_path_of_file(self, root_path: Path) -> None:
        self._root_directory_path = root_path

    def validate(self, value: str) -> ValidationResult:
        mode_validators: dict[FilePathValidator.Modes, tuple[Callable[[str], bool], str]] = {
            "is_file": (validate_path_is_file, self.NOT_A_FILE_FAILURE_DESC),
            "is_file_or_can_be_file": (
                validate_is_file_or_can_be_file,
                self.NOT_A_FILE_OR_CANT_BE_FILE_FAILURE_DESC,
            ),
        }

        validators = [Function(validate_filename, self.NOT_A_PROPER_FILE_NAME)]

        method = mode_validators[self.mode][0]
        desc = mode_validators[self.mode][1]
        validators += [Function(method, desc)]

        validation_results: list[ValidationResult] = []
        for validator in validators:
            if validator.function is validate_filename:
                # We need to explicitly check the raw filename passed to validation.
                # If we passed it as a Path, it would return True for scenarios
                # where there is a slash / in the filename, as it would be interpreted as a directory separator.
                # Example:
                # some/wrong.name -> Path("some/wrong.name").name would return "wrong.name"
                validation_results.append(validator.validate(value))
            else:
                validation_results.append(validator.validate(self._get_filepath(value)))
        return ValidationResult.merge(validation_results)

    def _get_filepath(self, value: str) -> str:
        return str(self._root_directory_path / Path(value))

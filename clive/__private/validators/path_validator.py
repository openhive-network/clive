from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal

from textual.validation import Function, ValidationResult, Validator

from clive.__private.validators.filesystem_validation_tools import (
    validate_can_be_directory,
    validate_can_be_file,
    validate_is_directory_or_can_be_directory,
    validate_is_file_or_can_be_file,
    validate_is_file_or_directory,
    validate_path,
    validate_path_exists,
    validate_path_is_directory,
    validate_path_is_file,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class PathValidator(Validator):
    INVALID_FAILURE_DESC: Final[str] = "Path is invalid (couldn't resolve)."

    NOT_EXISTS_FAILURE_DESC: Final[str] = "Path does not exist."
    NOT_A_FILE_FAILURE_DESC: Final[str] = "Path should be a file"
    NOT_A_DIRECTORY_FAILURE_DESC: Final[str] = "Path should be a directory."
    NOT_A_FILE_OR_DIRECTORY_FAILURE_DESC: Final[str] = "Path should be a file or a directory."

    CANT_BE_FILE_FAILURE_DESC: Final[str] = "Path can't be a file."
    CANT_BE_DIRECTORY_FAILURE_DESC: Final[str] = "Path can't be a directory."

    NOT_A_FILE_OR_CANT_BE_FILE_FAILURE_DESC: Final[str] = "Path is not a file or can't be a file."
    NOT_A_DIRECTORY_OR_CANT_BE_DIRECTORY_FAILURE_DESC: Final[str] = "Path is not a directory or can't be a directory."

    type Modes = Literal[
        "is_valid",
        "exists",
        "is_file",
        "is_directory",
        "is_file_or_directory",
        "can_be_file",
        "can_be_directory",
        "is_file_or_can_be_file",
        "is_directory_or_can_be_directory",
    ]
    """
    All modes implicitly include `is_valid` mode.

    is_file, is_directory, is_file_or_directory, already implicitly include `exists` mode.
    """

    def __init__(self, mode: Modes) -> None:
        super().__init__()
        self.mode = mode

    def validate(self, value: str) -> ValidationResult:
        mode_validators: dict[PathValidator.Modes, tuple[Callable[[str], bool], str]] = {
            "exists": (validate_path_exists, self.NOT_EXISTS_FAILURE_DESC),
            "is_file": (validate_path_is_file, self.NOT_A_FILE_FAILURE_DESC),
            "is_directory": (validate_path_is_directory, self.NOT_A_DIRECTORY_FAILURE_DESC),
            "is_file_or_directory": (validate_is_file_or_directory, self.NOT_A_FILE_OR_DIRECTORY_FAILURE_DESC),
            "can_be_file": (validate_can_be_file, self.CANT_BE_FILE_FAILURE_DESC),
            "can_be_directory": (validate_can_be_directory, self.CANT_BE_DIRECTORY_FAILURE_DESC),
            "is_file_or_can_be_file": (
                validate_is_file_or_can_be_file,
                self.NOT_A_FILE_OR_CANT_BE_FILE_FAILURE_DESC,
            ),
            "is_directory_or_can_be_directory": (
                validate_is_directory_or_can_be_directory,
                self.NOT_A_DIRECTORY_OR_CANT_BE_DIRECTORY_FAILURE_DESC,
            ),
        }

        validators = [Function(validate_path, self.INVALID_FAILURE_DESC)]

        method = mode_validators[self.mode][0]
        desc = mode_validators[self.mode][1]
        validators += [Function(method, desc)]

        return ValidationResult.merge([validator.validate(value) for validator in validators])

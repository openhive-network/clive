from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal

from textual.validation import Function, ValidationResult, Validator

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
            "exists": (self._validate_path_exists, self.NOT_EXISTS_FAILURE_DESC),
            "is_file": (self._validate_path_is_file, self.NOT_A_FILE_FAILURE_DESC),
            "is_directory": (self._validate_path_is_directory, self.NOT_A_DIRECTORY_FAILURE_DESC),
            "is_file_or_directory": (self._validate_is_file_or_directory, self.NOT_A_FILE_OR_DIRECTORY_FAILURE_DESC),
            "can_be_file": (self._validate_can_be_file, self.CANT_BE_FILE_FAILURE_DESC),
            "can_be_directory": (self._validate_can_be_directory, self.CANT_BE_DIRECTORY_FAILURE_DESC),
            "is_file_or_can_be_file": (
                self._validate_is_file_or_can_be_file,
                self.NOT_A_FILE_OR_CANT_BE_FILE_FAILURE_DESC,
            ),
            "is_directory_or_can_be_directory": (
                self._validate_is_directory_or_can_be_directory,
                self.NOT_A_DIRECTORY_OR_CANT_BE_DIRECTORY_FAILURE_DESC,
            ),
        }

        validators = [Function(self._validate_path, self.INVALID_FAILURE_DESC)]

        method = mode_validators[self.mode][0]
        desc = mode_validators[self.mode][1]
        validators += [Function(method, desc)]

        return ValidationResult.merge([validator.validate(value) for validator in validators])

    def _validate_path(self, value: str) -> bool:
        try:
            Path(value).resolve()
        except (OSError, RuntimeError):
            return False
        return True

    def _validate_path_exists(self, value: str) -> bool:
        return Path(value).exists()

    def _validate_path_is_file(self, value: str) -> bool:
        return Path(value).is_file()

    def _validate_path_is_directory(self, value: str) -> bool:
        return Path(value).is_dir()

    def _validate_is_file_or_directory(self, value: str) -> bool:
        return self._validate_path_is_file(value) or self._validate_path_is_directory(value)

    def _validate_can_be_file(self, value: str) -> bool:
        return not self._validate_path_is_directory(value)

    def _validate_can_be_directory(self, value: str) -> bool:
        return not self._validate_path_is_file(value)

    def _validate_is_file_or_can_be_file(self, value: str) -> bool:
        return self._validate_path_is_file(value) or self._validate_can_be_file(value)

    def _validate_is_directory_or_can_be_directory(self, value: str) -> bool:
        return self._validate_path_is_directory(value) or self._validate_can_be_directory(value)

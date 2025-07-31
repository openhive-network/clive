from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.tui.placeholders import FILE_NAME_PLACEHOLDER
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.validators.file_path_validator import FilePathValidator

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from textual.suggester import Suggester
    from textual.widgets._input import InputValidationOn


class FileNameInput(TextInput):
    """
    An input for a file name.

    Args:
        root_directory_path: A path to the root directory of the file.
        title: The title of the input.
        value: The initial value of the input.
        placeholder: Placeholder text for the input.
        always_show_title: Whether to always show the title (by default it is shown only when focused).
        include_title_in_placeholder_when_blurred: Whether to include the title in the placeholder when blurred.
        show_invalid_reasons: Whether to show reasons for invalid input.
        required: Whether the input is required.
        suggester: A suggester for auto-completion.
        validator_mode: The mode of the validator to use.
        validate_on: When to validate the input.
        valid_empty: Whether an empty input is considered as valid.
        id: The ID of the input in the DOM.
        classes: The CSS classes for the input.
        disabled: Whether the input is disabled.
    """

    def __init__(
        self,
        root_directory_path: Path,
        title: str = "File name",
        value: str | Path | None = None,
        placeholder: str = FILE_NAME_PLACEHOLDER,
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
        suggester: Suggester | None = None,
        validator_mode: FilePathValidator.Modes = "is_file",
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            title=title,
            value=str(value) if value is not None else None,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            suggester=suggester,
            validators=[FilePathValidator(mode=validator_mode, root_directory_path=root_directory_path)],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._root_directory_path = root_directory_path

    @property
    def root_directory_path(self) -> Path:
        return self._root_directory_path

    @property
    def filepath(self) -> Path | None:
        filename = self.value_or_none()
        return self._root_directory_path / filename if filename else None

    def update_root_directory_path(self, root_path: Path) -> None:
        self._update_file_path_validator(root_path)
        self._update_root_directory_path(root_path)

    def _update_root_directory_path(self, root_path: Path) -> None:
        self._root_directory_path = root_path

    def _update_file_path_validator(self, root_path: Path) -> None:
        for validator in self.input.validators:
            if isinstance(validator, FilePathValidator):
                validator.update_root_directory_path(root_path)

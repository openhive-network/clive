from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from clive.__private.core.constants.tui.placeholders import PATH_PLACEHOLDER
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    CliveValidatedInput,
)
from clive.__private.validators.path_validator import PathValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.suggester import Suggester
    from textual.widgets._input import InputValidationOn


class PathInput(CliveValidatedInput[Path]):
    """
    An input for a file system path.

    Args:
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
        title: str = "File path",
        value: str | Path | None = None,
        placeholder: str = PATH_PLACEHOLDER,
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
        suggester: Suggester | None = None,
        validator_mode: PathValidator.Modes = "is_valid",
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
            type="text",
            validators=[PathValidator(mode=validator_mode)],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @property
    def _value(self) -> Path:
        return Path(self.value_raw)

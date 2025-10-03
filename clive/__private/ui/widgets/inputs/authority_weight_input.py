from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.tui.placeholders import INTEGER_PLACEHOLDER
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.validators.authority_weight_validator import AuthorityWeightValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class AuthorityWeightInput(IntegerInput):
    """
    Input for authority weight.

    Args:
        value: The initial value of the input.
        placeholder: Placeholder text for the input.
        always_show_title: Whether to always show the title (by default it is shown only when focused).
        include_title_in_placeholder_when_blurred: Whether to include the title in the placeholder when blurred.
        show_invalid_reasons: Whether to show reasons for invalid input.
        required: Whether the input is required.
        validators: Validators for the input.
        validate_on: When to validate the input.
        valid_empty: Whether an empty input is considered as valid.
        id: The ID of the input in the DOM.
        classes: The CSS classes for the input.
        disabled: Whether the input is disabled.
    """

    def __init__(
        self,
        value: str | int | None = None,
        placeholder: str = INTEGER_PLACEHOLDER,
        *,
        always_show_title: bool = True,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
        validators: Validator | Iterable[Validator] | None = None,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            title="Weight",
            value=str(value) if value is not None else None,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            validators=validators or [AuthorityWeightValidator()],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

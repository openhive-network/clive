from __future__ import annotations

from typing import TYPE_CHECKING

from textual.validation import Number

from clive.__private.ui.widgets.inputs.numeric_input import NumericInput

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.widgets._input import InputValidationOn

    from clive.__private.core.decimal_conventer import DecimalConvertible


class PercentInput(NumericInput):
    """
    An input for a values between 0.01 and 100.

    Args:
        title: The title of the input.
        value: The initial value of the input, can be a DecimalConvertible or None.
        always_show_title: Whether to always show the title.
        include_title_in_placeholder_when_blurred: Whether to include the title when the input is blurred.
        show_invalid_reasons: Whether to show reasons for invalid input.
        required: Whether the input is required.
        validate_on: When to validate the input.
        valid_empty: Whether the input can be valid when empty.
        id: The ID of the input widget.
        classes: Additional CSS classes for the input.
        disabled: Whether the input is disabled.
    """

    def __init__(
        self,
        title: str = "Percent",
        value: DecimalConvertible | None = None,
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            title=title,
            value=value,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            validators=Number(minimum=0.01, maximum=100),
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

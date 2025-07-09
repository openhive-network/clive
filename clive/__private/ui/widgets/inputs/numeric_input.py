from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from clive.__private.core.decimal_conventer import DecimalConverter, DecimalConvertible
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class NumericInput(CliveValidatedInput[Decimal]):
    """
    An input for a numeric value.

    Args:
        title: The title of the input.
        value: The initial value of the input.
        placeholder: Placeholder text for the input.
        precision: Maximum allowed precision for the numeric value.
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

    Raises:
        ValueError: If precision is less than 1. IntegerInput should be used instead.
    """

    def __init__(
        self,
        title: str,
        value: DecimalConvertible | None = None,
        placeholder: str = "",
        *,
        precision: int = 2,
        always_show_title: bool = False,
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
        if precision < 1:
            raise ValueError("Precision should be at least 1. Instead use a IntegerInput.")

        super().__init__(
            title=title,
            value=str(DecimalConverter.convert(value)) if value is not None else None,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            restrict=self._create_restriction(precision),
            type="number",
            validators=validators,
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @property
    def _value(self) -> Decimal:
        return DecimalConverter.convert(self.value_raw)

    @staticmethod
    def _create_restriction(precision: int) -> str:
        precision_digits = f"{{0,{precision}}}"
        return rf"\d*\.?\d{precision_digits}"

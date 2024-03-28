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
    """An input for a numeric value."""

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
        """
        Initialise the widget.

        New args (compared to `CliveValidatedInput`):
        ------------------------------------
        precision: Maximum allowed precision, enforced by restriction.
        """
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

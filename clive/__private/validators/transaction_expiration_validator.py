from __future__ import annotations

from typing import Final

from textual.validation import Function, ValidationResult, Validator

from clive.__private.core.constants.date import (
    TRANSACTION_EXPIRATION_TIMEDELTA_MAX,
    TRANSACTION_EXPIRATION_TIMEDELTA_MIN,
)
from clive.__private.core.shorthand_timedelta import (
    SHORTHAND_TIMEDELTA_EXAMPLE_SHORT,
    InvalidShorthandToTimedeltaError,
    shorthand_timedelta_to_timedelta,
    timedelta_to_shorthand_timedelta,
)


class TransactionExpirationValidator(Validator):
    """
    Validates given transaction expiration value.

    Attributes:
        INVALID_INPUT_DESCRIPTION: Description for invalid input.
        VALUE_TOO_SMALL_DESCRIPTION: Description for value that is too small.
        VALUE_TOO_LARGE_DESCRIPTION: Description for value that is too large.
    """

    INVALID_INPUT_DESCRIPTION: Final[str] = (
        f"Incorrect format, must be one of the following {SHORTHAND_TIMEDELTA_EXAMPLE_SHORT}"
    )
    VALUE_TOO_SMALL_DESCRIPTION: Final[str] = (
        f"Value must be greater or equal {timedelta_to_shorthand_timedelta(TRANSACTION_EXPIRATION_TIMEDELTA_MIN)}."
    )
    VALUE_TOO_LARGE_DESCRIPTION: Final[str] = (
        f"Value must be less or equal {timedelta_to_shorthand_timedelta(TRANSACTION_EXPIRATION_TIMEDELTA_MAX)}."
    )

    def validate(self, value: str) -> ValidationResult:
        validators = [
            Function(self._validate_raw_input, self.INVALID_INPUT_DESCRIPTION),
            Function(self._validate_min_value, self.VALUE_TOO_SMALL_DESCRIPTION),
            Function(self._validate_max_value, self.VALUE_TOO_LARGE_DESCRIPTION),
        ]

        return ValidationResult.merge([validator.validate(value) for validator in validators])

    def _validate_raw_input(self, value: str) -> bool:
        try:
            shorthand_timedelta_to_timedelta(value)
        except InvalidShorthandToTimedeltaError:
            return False
        return True

    def _validate_min_value(self, value: str) -> bool:
        try:
            calculated_value = shorthand_timedelta_to_timedelta(value)
            if calculated_value < TRANSACTION_EXPIRATION_TIMEDELTA_MIN:
                return False
        except InvalidShorthandToTimedeltaError:
            return True
        return True

    def _validate_max_value(self, value: str) -> bool:
        try:
            calculated_value = shorthand_timedelta_to_timedelta(value)
            if calculated_value > TRANSACTION_EXPIRATION_TIMEDELTA_MAX:
                return False
        except InvalidShorthandToTimedeltaError:
            return True
        return True

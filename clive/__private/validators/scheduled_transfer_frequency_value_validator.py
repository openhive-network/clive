from __future__ import annotations

from typing import Final

from textual.validation import Function, ValidationResult, Validator

from clive.__private.core.constants.node import SCHEDULED_TRANSFER_MINIMUM_FREQUENCY_VALUE
from clive.__private.core.shorthand_timedelta import (
    SHORTHAND_TIMEDELTA_EXAMPLE,
    InvalidShorthandToTimedeltaError,
    shorthand_timedelta_to_timedelta,
    timedelta_to_shorthand_timedelta,
)


class ScheduledTransferFrequencyValidator(Validator):
    """
    Validates given frequency value.

    Used e.g. in transfer-schedule commands, in the recurrent transfer operation as "recurrence".

    Attributes:
        INVALID_INPUT_DESCRIPTION: Description for invalid input.
        VALUE_TO_SMALL_DESCRIPTION: Description for value that is too small.
    """

    INVALID_INPUT_DESCRIPTION: Final[str] = (
        f"Incorrect frequency unit must be one of the following {SHORTHAND_TIMEDELTA_EXAMPLE}"
    )
    VALUE_TO_SMALL_DESCRIPTION: Final[str] = (
        "Value for 'frequency' must be greater or equal "
        f"{timedelta_to_shorthand_timedelta(SCHEDULED_TRANSFER_MINIMUM_FREQUENCY_VALUE)}."
    )

    def validate(self, value: str) -> ValidationResult:
        validators = [
            Function(self._validate_raw_input, self.INVALID_INPUT_DESCRIPTION),
            Function(self._validate_calculated_value, self.VALUE_TO_SMALL_DESCRIPTION),
        ]

        return ValidationResult.merge([validator.validate(value) for validator in validators])

    def _validate_raw_input(self, value: str) -> bool:
        try:
            shorthand_timedelta_to_timedelta(value)
        except InvalidShorthandToTimedeltaError:
            return False
        return True

    def _validate_calculated_value(self, value: str) -> bool:
        try:
            calculated_value = shorthand_timedelta_to_timedelta(value)
            if calculated_value < SCHEDULED_TRANSFER_MINIMUM_FREQUENCY_VALUE:
                return False
        except InvalidShorthandToTimedeltaError:
            # Why True after this line?
            # Because this function is only to validate calculated value.
            # If input was wrong, then _validate_raw_input, returns proper message.
            return True
        return True

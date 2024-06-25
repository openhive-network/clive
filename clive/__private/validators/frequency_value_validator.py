from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Validator

from clive.__private.core.constants.node import SCHEDULED_TRANSFER_MINIMUM_FREQUENCY_VALUE
from clive.__private.core.shorthand_timedelta import shorthand_timedelta_to_timedelta, timedelta_to_shorthand_timedelta

if TYPE_CHECKING:
    from datetime import timedelta

    from textual.validation import ValidationResult


class FrequencyValueValidator(Validator):
    """
    Validates given frequency value.

    Used e.g. in transfer-schedule commands, in the recurrent transfer operation as "recurrence".
    """

    INVALID_INPUT_DESCRIPTION: Final[str] = (
        'Incorrect frequency unit must be one of the following hH, dD, wW. (e.g. "24h" or "2d 2h")'
    )
    VALUE_TO_SMALL_DESCRIPTION: Final[str] = (
        "Value for 'frequency' must be greater or equal "
        f"{timedelta_to_shorthand_timedelta(SCHEDULED_TRANSFER_MINIMUM_FREQUENCY_VALUE)}."
    )

    def __init__(self) -> None:
        super().__init__()

    def validate(self, value: str) -> ValidationResult:
        td = self._validate_raw_input(value)
        if td and self._validate_calculated_value(td):
            return self.success()

        return self.failure(description=self.failure_description)

    def _validate_raw_input(self, input_frequency: str) -> timedelta | None:
        try:
            return shorthand_timedelta_to_timedelta(input_frequency.lower())
        except ValueError:
            self.failure_description = self.INVALID_INPUT_DESCRIPTION
        return None

    def _validate_calculated_value(self, calculated_frequency: timedelta) -> bool:
        if calculated_frequency < SCHEDULED_TRANSFER_MINIMUM_FREQUENCY_VALUE:
            self.failure_description = self.VALUE_TO_SMALL_DESCRIPTION
            return False
        return True

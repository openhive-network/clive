from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.validation import Validator

if TYPE_CHECKING:
    from textual.validation import ValidationResult

    from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput


class RepeatValidator(Validator):
    """
    Validator which checks if same text is repeated as in the provided input.

    Args:
        input_to_repeat: The input whose value should be repeated.
        failure_description: The description of the failure if the validation fails.
    """

    def __init__(
        self,
        input_to_repeat: CliveValidatedInput[Any],
        failure_description: str,
    ) -> None:
        super().__init__()

        self.input_to_repeat = input_to_repeat
        self.failure_description = failure_description

    def validate(self, value: str) -> ValidationResult:
        if self._validate_is_repeated(value):
            return self.success()

        return self.failure(self.failure_description, value)

    def _validate_is_repeated(self, value: str) -> bool:
        return self.input_to_repeat.value_raw == value

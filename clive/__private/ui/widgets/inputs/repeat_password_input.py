from __future__ import annotations

from typing import TYPE_CHECKING, Any

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.validators.repeat_validator import RepeatValidator

if TYPE_CHECKING:
    from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput


class RepeatPasswordInput(TextInput):
    """
    Specialized TextInput for repeat password.

    Args:
        input_to_repeat: The input to repeat the password against.
    """

    def __init__(self, input_to_repeat: CliveValidatedInput[Any]) -> None:
        super().__init__(
            "Repeat password",
            password=True,
            validators=[RepeatValidator(input_to_repeat=input_to_repeat, failure_description="Passwords do not match")],
        )

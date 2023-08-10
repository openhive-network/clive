from __future__ import annotations

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import WITNESS_PLACEHOLDER


class WitnessInput(TextInput):
    def __init__(
        self, label: str = "witness", value: str | None = None, placeholder: str = WITNESS_PLACEHOLDER
    ) -> None:
        super().__init__(label=label, value=value, placeholder=placeholder)

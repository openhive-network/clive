from __future__ import annotations

import json

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import JSON_DATA_PLACEHOLDER

AnyJsonT = None | bool | str | int | float | list["AnyJsonT"] | dict[str, "AnyJsonT"]


class JsonDataInput(CustomInput[AnyJsonT]):
    def __init__(
        self,
        label: str = "json metadata",
        value: AnyJsonT | None = None,
        placeholder: str = JSON_DATA_PLACEHOLDER,
    ) -> None:
        super().__init__(label=label, value=value, placeholder=placeholder)

    @property
    def value(self) -> AnyJsonT:
        json_value: AnyJsonT = json.loads(self._input.value)
        return json_value

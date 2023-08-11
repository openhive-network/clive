from __future__ import annotations

import json
from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import JSON_DATA_PLACEHOLDER

if TYPE_CHECKING:
    from textual.widget import Widget

AnyJsonT = None | bool | str | int | float | list["AnyJsonT"] | dict[str, "AnyJsonT"]


class JsonDataInput(CustomInput[AnyJsonT]):
    def __init__(
        self,
        to_mount: Widget,
        label: str = "json metadata",
        value: AnyJsonT | None = None,
        placeholder: str = JSON_DATA_PLACEHOLDER,
    ) -> None:
        super().__init__(to_mount=to_mount, label=label, value=value, placeholder=placeholder)

    @property
    def value(self) -> AnyJsonT:
        json_value: AnyJsonT = json.loads(self._input.value)
        return json_value

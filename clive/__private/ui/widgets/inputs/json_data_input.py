from __future__ import annotations

import json
from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import JSON_DATA_PLACEHOLDER

if TYPE_CHECKING:
    from rich.console import RenderableType

AnyJsonT = None | bool | str | int | float | list["AnyJsonT"] | dict[str, "AnyJsonT"]


class JsonDataInput(CustomInput[AnyJsonT]):
    def __init__(
        self,
        label: str = "json metadata",
        value: AnyJsonT | None = None,
        *,
        placeholder: str = JSON_DATA_PLACEHOLDER,
        tooltip: RenderableType | None = None,
        disabled: bool = False,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            label=label,
            value=value,
            placeholder=placeholder,
            tooltip=tooltip,
            disabled=disabled,
            id_=id_,
            classes=classes,
        )

    @property
    def value(self) -> AnyJsonT:
        json_value: AnyJsonT = json.loads(self._input.value)
        return json_value

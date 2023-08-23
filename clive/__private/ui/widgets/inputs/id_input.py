from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.placeholders_constants import ID_PLACEHOLDER

if TYPE_CHECKING:
    from rich.console import RenderableType


class IdInput(IntegerInput):
    def __init__(
        self,
        label: str = "id",
        value: int | None = None,
        *,
        placeholder: str = ID_PLACEHOLDER,
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

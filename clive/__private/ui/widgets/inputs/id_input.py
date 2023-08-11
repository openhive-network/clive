from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.placeholders_constants import ID_PLACEHOLDER

if TYPE_CHECKING:
    from textual.widget import Widget


class IdInput(IntegerInput):
    """To use this input specify by generic one of above type of id."""

    def __init__(
        self, to_mount: Widget, label: str = "id", value: int | None = None, placeholder: str = ID_PLACEHOLDER
    ) -> None:
        super().__init__(to_mount=to_mount, label=label, value=value, placeholder=placeholder)

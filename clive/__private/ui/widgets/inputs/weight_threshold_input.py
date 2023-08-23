from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.validate_schema_field import is_schema_field_valid
from clive.__private.ui.widgets.clive_highlighter import CliveHighlighter
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.placeholders_constants import INTEGER_PLACEHOLDER
from schemas.__private.hive_fields_basic_schemas import Uint32t

if TYPE_CHECKING:
    from rich.console import RenderableType


class WeightThresholdHighlighter(CliveHighlighter):
    def is_valid_value(self, value: str) -> bool:
        return is_schema_field_valid(Uint32t, value)


class WeightThresholdInput(IntegerInput):
    def __init__(
        self,
        label: str = "weight threshold",
        value: int | None = None,
        *,
        placeholder: str = INTEGER_PLACEHOLDER,
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
            highlighter=WeightThresholdHighlighter(),
            id_=id_,
            classes=classes,
        )

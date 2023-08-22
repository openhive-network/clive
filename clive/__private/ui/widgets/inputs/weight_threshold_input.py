from __future__ import annotations

from clive.__private.core.validate_schema_field import is_schema_field_valid
from clive.__private.ui.widgets.clive_highlighter import CliveHighlighter
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from schemas.__private.hive_fields_basic_schemas import Uint32t


class WeightThresholdHighlighter(CliveHighlighter):
    def is_valid_value(self, value: str) -> bool:
        return is_schema_field_valid(Uint32t, value)


class WeightThresholdInput(IntegerInput):
    def __init__(self, label: str = "weight threshold", value: int | None = None) -> None:
        super().__init__(label=label, value=value, highlighter=WeightThresholdHighlighter())

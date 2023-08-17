from __future__ import annotations

from pydantic import ValidationError

from clive.__private.core.validate_schema_field import validate_schema_field
from clive.__private.ui.widgets.clive_highlighter import CliveHighlighter
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from schemas.__private.hive_fields_basic_schemas import Uint32t


class WeightThresholdHighlighter(CliveHighlighter):
    def is_valid_value(self, value: str) -> bool:
        try:
            validate_schema_field(Uint32t, value)
        except ValidationError:
            return False
        else:
            return True


class WeightThresholdInput(IntegerInput):
    def __init__(self, label: str = "weight threshold", value: int | None = None) -> None:
        super().__init__(label=label, value=value, highlighter=WeightThresholdHighlighter())

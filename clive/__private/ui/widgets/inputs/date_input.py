from __future__ import annotations

from datetime import datetime, timezone
from typing import Final

from pydantic import ValidationError

from clive.__private.core.validate_schema_field import validate_schema_field
from clive.__private.ui.widgets.clive_highlighter import CliveHighlighter
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import DATE_PLACEHOLDER
from schemas.__private.hive_fields_basic_schemas import HiveDateTime


class DateHighlighter(CliveHighlighter):
    def is_valid_value(self, value: str) -> bool:
        try:
            validate_schema_field(HiveDateTime, value)
        except ValidationError:
            return False
        else:
            return True


class DateInput(CustomInput[datetime]):
    DATE_TOOLTIP: Final[str] = "Notice: put date in ISO format e.g.: 2020-11-12T01:20:48"

    def __init__(self, label: str = "date", value: datetime | None = None, placeholder: str = DATE_PLACEHOLDER) -> None:
        super().__init__(
            label=label, value=value, placeholder=placeholder, tooltip=self.DATE_TOOLTIP, highlighter=DateHighlighter()
        )

    @property
    def value(self) -> datetime:
        return datetime.strptime(self._input.value, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)

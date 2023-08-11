from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.placeholders_constants import DATE_PLACEHOLDER

if TYPE_CHECKING:
    from textual.widget import Widget


class DateInput(CustomInput[datetime]):
    def __init__(
        self, to_mount: Widget, label: str = "date", value: datetime | None = None, placeholder: str = DATE_PLACEHOLDER
    ) -> None:
        super().__init__(to_mount=to_mount, label=label, value=value, placeholder=placeholder)

    @property
    def value(self) -> datetime:
        return datetime.strptime(self._input.value, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)

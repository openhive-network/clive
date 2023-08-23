from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.validate_schema_field import is_schema_field_valid
from clive.__private.ui.widgets.clive_highlighter import CliveHighlighter
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import PERMLINK_PLACEHOLDER
from schemas.__private.hive_fields_custom_schemas import Permlink

if TYPE_CHECKING:
    from rich.console import RenderableType


class PermlinkHighlighter(CliveHighlighter):
    def is_valid_value(self, value: str) -> bool:
        return is_schema_field_valid(Permlink, value)


class PermlinkInput(TextInput):
    def __init__(
        self,
        label: str = "permlink",
        value: str | None = None,
        *,
        placeholder: str = PERMLINK_PLACEHOLDER,
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
            highlighter=PermlinkHighlighter(),
            id_=id_,
            classes=classes,
        )

from __future__ import annotations

from clive.__private.core.validate_schema_field import is_schema_field_valid
from clive.__private.ui.widgets.clive_highlighter import CliveHighlighter
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import PERMLINK_PLACEHOLDER
from schemas.__private.hive_fields_custom_schemas import Permlink


class PermlinkHighlighter(CliveHighlighter):
    def is_valid_value(self, value: str) -> bool:
        return is_schema_field_valid(Permlink, value)


class PermlinkInput(TextInput):
    def __init__(
        self, label: str = "permlink", value: str | None = None, placeholder: str = PERMLINK_PLACEHOLDER
    ) -> None:
        super().__init__(label=label, value=value, placeholder=placeholder, highlighter=PermlinkHighlighter())

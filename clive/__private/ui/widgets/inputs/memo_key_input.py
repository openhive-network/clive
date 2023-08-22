from __future__ import annotations

from clive.__private.core.validate_schema_field import is_schema_field_valid
from clive.__private.ui.widgets.clive_highlighter import CliveHighlighter
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import KEY_PLACEHOLDER
from schemas.__private.hive_fields_basic_schemas import PublicKey


class MemoKeyHighlighter(CliveHighlighter):
    def is_valid_value(self, value: str) -> bool:
        return is_schema_field_valid(PublicKey, value)


class MemoKeyInput(TextInput):
    def __init__(self, label: str = "memo key", placeholder: str = KEY_PLACEHOLDER, value: str | None = None):
        super().__init__(label=label, placeholder=placeholder, value=value)

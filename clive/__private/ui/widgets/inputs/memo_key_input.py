from __future__ import annotations

from pydantic import ValidationError

from clive.__private.core.validate_schema_field import validate_schema_field
from clive.__private.ui.widgets.clive_highlighter import CliveHighlighter
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import KEY_PLACEHOLDER
from schemas.__private.hive_fields_basic_schemas import PublicKey


class MemoKeyHighlighter(CliveHighlighter):
    def is_valid_value(self, value: str) -> bool:
        try:
            validate_schema_field(PublicKey, value)
        except ValidationError:
            return False
        else:
            return True


class MemoKeyInput(TextInput):
    def __init__(self, label: str = "memo key", placeholder: str = KEY_PLACEHOLDER, value: str | None = None):
        super().__init__(label=label, placeholder=placeholder, value=value)

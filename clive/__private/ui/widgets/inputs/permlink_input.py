from __future__ import annotations

from pydantic import ValidationError

from clive.__private.core.validate_schema_field import validate_schema_field
from clive.__private.ui.widgets.clive_highlighter import CliveHighlighter
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import PERMLINK_PLACEHOLDER
from schemas.__private.hive_fields_custom_schemas import Permlink


class PermlinkHighlighter(CliveHighlighter):
    def is_valid_value(self, value: str) -> bool:
        try:
            validate_schema_field(Permlink, value)
        except ValidationError:
            return False
        else:
            return True


class PermlinkInput(TextInput):
    def __init__(
        self, label: str = "permlink", value: str | None = None, placeholder: str = PERMLINK_PLACEHOLDER
    ) -> None:
        super().__init__(label=label, value=value, placeholder=placeholder, highlighter=PermlinkHighlighter())

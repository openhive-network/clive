from __future__ import annotations

from pydantic import ValidationError

from clive.__private.core.validate_schema_field import validate_schema_field
from clive.__private.ui.widgets.clive_highlighter import CliveHighlighter
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_NAME_PLACEHOLDER
from schemas.__private.hive_fields_basic_schemas import AccountName


class AccountNameHighlighter(CliveHighlighter):
    def is_valid_value(self, value: str) -> bool:
        try:
            validate_schema_field(AccountName, value)
        except ValidationError:
            return False
        else:
            return True


class AccountNameInput(TextInput):
    def __init__(
        self,
        label: str = "account name",
        placeholder: str = ACCOUNT_NAME_PLACEHOLDER,
        value: str | None = None,
        id_: str | None = None,
    ) -> None:
        super().__init__(
            label=label,
            placeholder=placeholder,
            value=value,
            highlighter=AccountNameHighlighter(),
            id_=id_,
        )

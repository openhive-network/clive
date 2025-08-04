from __future__ import annotations

from typing import TYPE_CHECKING

from textual.validation import Length

from clive.__private.core.constants.tui.placeholders import ACCOUNT_NAME_PATTERN_PLACEHOLDER
from clive.__private.models.schemas import AccountName
from clive.__private.ui.widgets.inputs.text_input import TextInput

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.suggester import Suggester
    from textual.widgets._input import InputValidationOn


class AccountNamePatternInput(TextInput):
    """An input for a Hive account name pattern."""

    def __init__(
        self,
        title: str = "Account name pattern",
        value: str | None = None,
        placeholder: str = ACCOUNT_NAME_PATTERN_PLACEHOLDER,
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
        suggester: Suggester | None = None,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            title=title,
            value=value,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            suggester=suggester,
            validators=[
                Length(minimum=1, maximum=AccountName.meta().max_length),  # type: ignore[attr-defined]
            ],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

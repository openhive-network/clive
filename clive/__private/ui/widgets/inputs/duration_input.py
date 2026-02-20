from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from clive.__private.core.shorthand_timedelta import shorthand_timedelta_to_timedelta, timedelta_to_shorthand_timedelta
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn

DURATION_PLACEHOLDER = 'e.g. "30m" or "1h 30m"'


class DurationInput(CliveValidatedInput[timedelta]):
    def __init__(
        self,
        title: str,
        value: str | timedelta | None = None,
        placeholder: str = DURATION_PLACEHOLDER,
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
        validators: Validator | Iterable[Validator] | None = None,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            title=title,
            value=timedelta_to_shorthand_timedelta(value) if isinstance(value, timedelta) else value,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            type="text",
            validators=validators,
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @property
    def _value(self) -> timedelta:
        return shorthand_timedelta_to_timedelta(self.value_raw)

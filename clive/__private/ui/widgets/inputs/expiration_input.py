from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from clive.__private.core.constants.date import TIME_FORMAT_WITH_SECONDS
from clive.__private.core.shorthand_timedelta import (
    InvalidShorthandToTimedeltaError,
    shorthand_timedelta_to_timedelta,
    timedelta_to_shorthand_timedelta,
)
from clive.__private.models.schemas import HiveDateTime
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class ExpirationInput(CliveValidatedInput[timedelta | datetime]):
    def __init__(
        self,
        title: str,
        value: str | timedelta | datetime | None = None,
        placeholder: str = "",
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
            value=self._convert_value(value),
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

    @staticmethod
    def _convert_value(value: str | timedelta | datetime | None) -> str | None:
        if isinstance(value, timedelta):
            return timedelta_to_shorthand_timedelta(value)
        if isinstance(value, datetime):
            return value.strftime(TIME_FORMAT_WITH_SECONDS)
        return value

    @property
    def _value(self) -> timedelta | datetime:
        raw = self.value_raw
        try:
            return shorthand_timedelta_to_timedelta(raw)
        except InvalidShorthandToTimedeltaError:
            return HiveDateTime(raw)

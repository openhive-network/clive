from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.tui.placeholders import INTEGER_PLACEHOLDER
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class IntegerInput(CliveValidatedInput[int]):
    """An input for a integer value."""

    def __init__(
        self,
        title: str,
        value: str | int | None = None,
        placeholder: str = INTEGER_PLACEHOLDER,
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
        process_add_to_cart: bool = True,
    ) -> None:
        super().__init__(
            title=title,
            value=str(value) if value is not None else None,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            type="integer",
            validators=validators,
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
            process_add_to_cart=process_add_to_cart,
        )

    @property
    def _value(self) -> int:
        return int(self.value_raw)

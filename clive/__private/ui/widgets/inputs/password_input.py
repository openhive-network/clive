from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.text_input import TextInput

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class PasswordInput(TextInput):
    """An input for entering a Clive password."""

    def __init__(
        self,
        title: str = "Password",
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
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            password=True,
            validators=validators,
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

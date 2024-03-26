from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.validators.set_password_validator import SetPasswordValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.widgets._input import InputValidationOn


class SetPasswordInput(TextInput):
    """An input for setting a Clive password."""

    def __init__(
        self,
        title: str = "Password",
        value: str | None = None,
        placeholder: str = "",
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
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
            password=True,
            validators=[SetPasswordValidator()],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

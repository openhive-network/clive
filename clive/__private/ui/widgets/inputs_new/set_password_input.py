from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Length

from clive.__private.ui.widgets.inputs_new.text_input import TextInput

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.widgets._input import InputValidationOn


class SetPasswordInput(TextInput):
    """An input for setting a Clive password."""

    PASSWORD_MIN_LENGTH: Final[int] = 8
    PASSWORD_MAX_LENGTH: Final[int] = 64

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
            validators=[
                Length(minimum=self.PASSWORD_MIN_LENGTH, maximum=self.PASSWORD_MAX_LENGTH),
            ],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

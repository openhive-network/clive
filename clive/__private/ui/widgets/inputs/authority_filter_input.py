from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.widgets import Input

from clive.__private.core.iwax import calculate_public_key
from clive.__private.core.keys.keys import PrivateKey
from clive.__private.ui.widgets.inputs.text_input import TextInput

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.suggester import Suggester
    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class AuthorityFilterInput(TextInput):
    """An input for authority entry - Hive account name, public / private key or alias."""

    def __init__(
        self,
        title: str = "Authority entry account, public/private key or alias",
        value: str | None = None,
        placeholder: str = "",
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = False,
        suggester: Suggester | None = None,
        validators: Validator | Iterable[Validator] | None = None,
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
            validators=validators,
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @on(Input.Changed)
    def _replace_private_with_public_key(self, event: Input.Changed) -> None:
        value = event.value
        if PrivateKey.is_valid(value):
            self.input.value = calculate_public_key(value).value
            self.notify("Private key was converted to public key.")

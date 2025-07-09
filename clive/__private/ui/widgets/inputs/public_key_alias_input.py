from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.tui.placeholders import KEY_ALIAS_PLACEHOLDER, SETTING_KEY_ALIAS_PLACEHOLDER
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.validators.public_key_alias_validator import PublicKeyAliasValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.suggester import Suggester
    from textual.widgets._input import InputValidationOn

    from clive.__private.core.keys import KeyManager


class PublicKeyAliasInput(TextInput):
    """
    An input for a public key alias.

    Args:
        title: The title of the input.
        value: The initial value of the input.
        placeholder: Placeholder text for the input.
        always_show_title: Whether to always show the title (by default it is shown only when focused).
        include_title_in_placeholder_when_blurred: Whether to include the title in the placeholder when blurred.
        show_invalid_reasons: Whether to show reasons for invalid input.
        required: Whether the input is required.
        setting_key_alias: Whether setting public key alias or just getting key alias for other purpose.
        suggester: A suggester for auto-completion.
        key_manager: Key manager to use for validation. If not provided, the key manager
            from the world will be used.
        validate_on: When to validate the input.
        valid_empty: Whether an empty input is considered as valid.
        id: The ID of the input in the DOM.
        classes: The CSS classes for the input.
        disabled: Whether the input is disabled.
    """

    def __init__(
        self,
        title: str = "Key alias",
        value: str | None = None,
        placeholder: str | None = None,
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
        setting_key_alias: bool = False,
        suggester: Suggester | None = None,
        key_manager: KeyManager | None = None,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        key_manager = key_manager if key_manager is not None else self.profile.keys
        placeholder = (
            placeholder
            if placeholder is not None
            else (SETTING_KEY_ALIAS_PLACEHOLDER if setting_key_alias else KEY_ALIAS_PLACEHOLDER)
        )

        super().__init__(
            title=title,
            value=value,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            suggester=suggester,
            validators=[PublicKeyAliasValidator(key_manager, validate_like_adding_new=setting_key_alias)],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

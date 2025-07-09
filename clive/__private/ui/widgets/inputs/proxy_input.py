from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.tui.placeholders import ACCOUNT_NAME2_PLACEHOLDER
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.validators.proxy_validator import ProxyValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.suggester import Suggester
    from textual.widgets._input import InputValidationOn


class ProxyInput(AccountNameInput):
    """
    An input for a Hive proxy account name.

    Args:
        title: The title of the input.
        value: The initial value of the input.
        placeholder: Placeholder text for the input.
        always_show_title: Whether to always show the title (by default it is shown only when focused).
        include_title_in_placeholder_when_blurred: Whether to include the title in the placeholder when blurred.
        show_invalid_reasons: Whether to show reasons for invalid input.
        required: Whether the input is required.
        show_known_account: Whether to show known accounts with a specific style.
        setting_proxy: Whether setting proxy or just getting proxy for other purpose.
        suggester: A suggester for auto-completion.
        validate_on: When to validate the input.
        valid_empty: Whether an empty input is considered as valid.
        id: The ID of the input in the DOM.
        classes: The CSS classes for the input.
        disabled: Whether the input is disabled.
    """

    def __init__(
        self,
        title: str = "Proxy account name",
        value: str | None = None,
        placeholder: str = ACCOUNT_NAME2_PLACEHOLDER,
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
        show_known_account: bool = True,
        setting_proxy: bool = False,
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
            show_known_account=show_known_account,
            suggester=suggester,
            validators=ProxyValidator(self.profile.accounts, check_is_not_working_account=setting_proxy),
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

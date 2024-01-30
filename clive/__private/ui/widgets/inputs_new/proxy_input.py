from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs_new.account_name_input import AccountNameInput
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_NAME2_PLACEHOLDER
from clive.__private.validators.proxy_validator import ProxyValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.widgets._input import InputValidationOn


class ProxyInput(AccountNameInput):
    """An input for a Hive proxy account name."""

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
        ask_known_account: bool = True,
        setting_proxy: bool = False,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """
        Initialise the widget.

        New args (compared to `CliveInput`):
        ------------------------------------
        setting_proxy: Whether setting proxy or just getting proxy for other purpose.
        """
        working_account_name = self.app.world.profile_data.working_account.name
        super().__init__(
            title=title,
            value=value,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            ask_known_account=ask_known_account,
            validators=[ProxyValidator(working_account_name if setting_proxy else None)],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

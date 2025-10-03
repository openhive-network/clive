from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.accounts.exceptions import AccountNotFoundError
from clive.__private.core.authority.entries import AuthorityEntryBase
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.validators.authority_entry_validator import AuthorityEntryValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.suggester import Suggester
    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class AuthorityEntryInput(TextInput):
    """
    Input for regular authority entry value - key or account.

    Args:
        title: The title of the input.
        value: The initial value of the input.
        placeholder: Placeholder text for the input.
        always_show_title: Whether to always show the title (by default it is shown only when focused).
        include_title_in_placeholder_when_blurred: Whether to include the title in the placeholder when blurred.
        show_invalid_reasons: Whether to show reasons for invalid input.
        required: Whether the input is required.
        suggester: A suggester for auto-completion.
        validators: Validators for the input.
        validate_on: When to validate the input.
        valid_empty: Whether an empty input is considered as valid.
        id: The ID of the input in the DOM.
        classes: The CSS classes for the input.
        disabled: Whether the input is disabled.
    """

    def __init__(
        self,
        title: str = "Account or public key",
        value: str | None = None,
        placeholder: str = "",
        *,
        always_show_title: bool = True,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
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
            validators=validators if validators else AuthorityEntryValidator(),
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @property
    def holds_account_name(self) -> bool:
        entry_type = AuthorityEntryBase.determine_entry_type(self.input.value)
        return entry_type == "account"

    async def validate_account_existence_in_node(self) -> None:
        """
        Verify if the account name entered exists in the connected node.

        Raises:
            AccountNotFoundError: When account was not found in the node.
        """
        if self.holds_account_name:
            account_name = self.input.value
            if not await self.app.does_account_exist_in_node(account_name=account_name):
                raise AccountNotFoundError(account_name=account_name)

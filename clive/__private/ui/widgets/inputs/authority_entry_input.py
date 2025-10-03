from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.validators.authority_entry_validator import AuthorityEntryValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.suggester import Suggester
    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class AuthorityEntryInput(TextInput):
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
        value = self.input.value
        if value:
            return not value.startswith("STM")
        return False

    async def validate_account_existence_in_node(self) -> bool:
        """
        Verify if the account name entered exists in the connected node.

        Returns:
            bool: True if the account exists or if the input is a public key, False otherwise.
        """
        if self.holds_account_name:
            account_name = self.input.value
            wrapper = await self.commands.does_account_exists_in_node(account_name=account_name)
            if wrapper.error_occurred:
                self.notify(f"Failed to check if account `{account_name}` exists in the node.")
                return False

            if not wrapper.result_or_raise:
                self.notify("Account not found in the node.", severity="error")
                return False
        return True

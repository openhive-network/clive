from __future__ import annotations

from typing import TYPE_CHECKING

from textual.message import Message

from clive.__private.core.constants.tui.placeholders import ACCOUNT_NAME_PLACEHOLDER
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.validators.bad_account_validator import BadAccountValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class ReceiverInput(AccountNameInput):
    """An input for a receiver that support additionally known exchange accounts."""

    class KnownExchangeDetected(Message):
        """Sent when a known exchange account is detected in the input."""

    class KnownExchangeGone(Message):
        """When an exchange account is no longer present in the input."""

    def __init__(
        self,
        title: str = "Account name",
        value: str | None = None,
        placeholder: str = ACCOUNT_NAME_PLACEHOLDER,
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
        show_known_account: bool = True,
        show_bad_account: bool = True,
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
            validators=validators or [BadAccountValidator(self.profile.accounts)],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
            show_bad_account=show_bad_account,
            show_known_account=show_known_account,
        )
        self._was_known_exchange_in_input = False

    def _handle_valid_account_name(self) -> None:
        if self.value_raw in self.world.known_exchanges:
            self.post_message(self.KnownExchangeDetected())
            self._change_input_style(
                self._KNOWN_ACCOUNT_CLASS,
                f"known exchange ({self.world.known_exchanges.get_entity_by_account_name(self.value_raw)})",
            )
            self._was_known_exchange_in_input = True
            return

        if self._was_known_exchange_in_input:
            self._was_known_exchange_in_input = False
            self.post_message(self.KnownExchangeGone())

        super()._handle_valid_account_name()

    def _handle_invalid_account_name(self) -> None:
        if self._was_known_exchange_in_input:
            self._was_known_exchange_in_input = False
            self.post_message(self.KnownExchangeGone())

        super()._handle_invalid_account_name()

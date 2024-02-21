from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Horizontal, Vertical

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.known_account import KnownAccount
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_NAME_PLACEHOLDER
from clive.__private.validators.account_name_validator import AccountNameValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.app import ComposeResult
    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class AccountNameInput(TextInput):
    """An input for a Hive account name."""

    _KNOWN_ACCOUNT_CLASS: Final[str] = "-known-account"
    _UNKNOWN_ACCOUNT_CLASS: Final[str] = "-unknown-account"

    DEFAULT_CSS = """
    AccountNameInput {
      height: auto;

      Vertical {
        height: auto;

        Horizontal {
          height: auto;

          CliveInput {
            width: 1fr;

            &.-known-account {
              border-subtitle-background: $success-darken-3;

            }

            &.-unknown-account {
              border-subtitle-background: $warning-lighten-1;
              border-subtitle-color: black;
            }
          }

          KnownAccount {
            width: 14;
          }
        }
      }
    }
    """

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
        ask_known_account: bool = True,
        validators: Validator | Iterable[Validator] | None = None,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """
        Initialize the widget.

        New args (compared to `TextInput`):
        ------------------------------------
        ask_known_account: Whether to display the KnownAccount widget which keeps track of know accounts list.
        """
        super().__init__(
            title=title,
            value=value,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            validators=validators or [AccountNameValidator()],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._ask_known_account = ask_known_account
        self._known_account = KnownAccount(self.input)

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield self.input
                if self._ask_known_account:
                    yield self._known_account
            yield self.pretty

    @on(KnownAccount.Status)
    def _update_known_account_status(self, event: KnownAccount.Status) -> None:
        known_account_text = "known account"
        unknown_account_text = "unknown account"

        is_account_known = event.is_account_known

        self.input.border_subtitle = known_account_text if is_account_known else unknown_account_text
        self.input.add_class(self._KNOWN_ACCOUNT_CLASS if is_account_known else self._UNKNOWN_ACCOUNT_CLASS)
        self.input.remove_class(self._UNKNOWN_ACCOUNT_CLASS if is_account_known else self._KNOWN_ACCOUNT_CLASS)
        self.input.refresh()  # sometimes it's not refreshed automatically without this..

    @on(KnownAccount.Disabled)
    def _remove_known_account_status(self) -> None:
        self.input.border_subtitle = ""
        self.input.remove_class(self._KNOWN_ACCOUNT_CLASS)
        self.input.remove_class(self._UNKNOWN_ACCOUNT_CLASS)

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Vertical
from textual.events import Mount

from clive.__private.core.accounts.accounts import Account
from clive.__private.core.constants.tui.placeholders import ACCOUNT_NAME_PLACEHOLDER
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.validators.bad_account_validator import BadAccountValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.app import ComposeResult
    from textual.suggester import Suggester
    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class AccountNameInput(TextInput):
    """An input for a Hive account name."""

    _KNOWN_ACCOUNT_CLASS: Final[str] = "-known-account"
    _UNKNOWN_ACCOUNT_CLASS: Final[str] = "-unknown-account"
    _BAD_ACCOUNT_CLASS: Final[str] = "-bad-account"

    DEFAULT_CSS = """
    AccountNameInput {
      height: auto;

      Vertical {
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

            &.-bad-account {
              border-subtitle-background: $error;
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
        show_known_account: bool = True,
        show_bad_account: bool = True,
        suggester: Suggester | None = None,
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
        accounts_holder: See the docs of `KnownAccount` initializer.
        """
        super().__init__(
            title=title,
            value=value,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            suggester=suggester,
            validators=validators or [BadAccountValidator(self.profile.accounts)],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._show_known_account = show_known_account
        self._show_bad_account = show_bad_account

    def compose(self) -> ComposeResult:
        with Vertical():
            yield self.input
            yield self.pretty

    @on(Mount)
    def _watch_input_value_change(self) -> None:
        if not self._show_known_account and not self._show_bad_account:
            return

        # >>> start workaround for Textual calling validate on input when self.watch is used. Setting validate_on to
        # values different from "changed" prevents this.
        before = self.input.validate_on
        self.input.validate_on = {"blur"}

        self.watch(self.input, "value", self._update_account_status)
        self.input.validate_on = before
        # <<< end workaround

    def add_account_to_known(self) -> None:
        """Add account to known accounts list if it's valid and not already known."""
        account_name = self.value_or_error

        if not self.profile.accounts.is_account_known(account_name):
            self.profile.accounts.known.add(account_name)

    def _change_input_style(self, css_class: str, border_subtitle: str) -> None:
        self.input.remove_class(self._UNKNOWN_ACCOUNT_CLASS, self._KNOWN_ACCOUNT_CLASS, self._BAD_ACCOUNT_CLASS)

        self.input.border_subtitle = border_subtitle
        self.input.add_class(css_class)
        self.input.refresh()  # sometimes it's not refreshed automatically without this..

    def _handle_valid_account_name(self) -> None:
        if self._show_bad_account and self.profile.accounts.is_account_bad(self.value_raw):
            self._change_input_style(self._BAD_ACCOUNT_CLASS, "BAD ACCOUNT!")
            return

        if not self._show_known_account:
            self.input.border_subtitle = ""
            self.input.refresh()  # sometimes it's not refreshed automatically without this..
            return

        if self.profile.accounts.is_account_known(self.value_raw):
            self._change_input_style(self._KNOWN_ACCOUNT_CLASS, "known account")
            return

        self._change_input_style(self._UNKNOWN_ACCOUNT_CLASS, "unknown account")

    def _handle_invalid_account_name(self) -> None:
        self.input.border_subtitle = None
        self.input.refresh()  # sometimes it's not refreshed automatically without this..

    def _update_account_status(self) -> None:
        if not Account.is_valid(self.value_raw):
            self._handle_invalid_account_name()
            return

        self._handle_valid_account_name()

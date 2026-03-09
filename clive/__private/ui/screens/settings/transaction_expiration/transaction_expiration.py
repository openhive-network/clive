from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Static

from clive.__private.core.shorthand_timedelta import shorthand_timedelta_to_timedelta, timedelta_to_shorthand_timedelta
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.inputs.clive_input import CliveInput
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.section import SectionScrollable
from clive.__private.validators.expiration_validator import ExpirationValidator, TimedeltaFormatParser

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult


class CurrentTransactionExpiration(Static):
    """Displays the current transaction expiration value.

    Args:
        expiration: The current expiration value.

    Attributes:
        expiration: The current expiration value.
    """

    expiration: str | None = reactive(None)  # type: ignore[assignment]

    def __init__(self, expiration: str) -> None:
        super().__init__()
        self.expiration = expiration

    def render(self) -> RenderableType:
        return f"Current transaction expiration: {self.expiration}"


class TransactionExpirationInput(TextInput):
    def __init__(self, current_value: str) -> None:
        super().__init__(
            "Transaction expiration",
            value=current_value,
            placeholder='e.g. "1h", "30m", "12h 30m" (min: 3s, max: 24h)',
            validators=ExpirationValidator(parsers=[TimedeltaFormatParser()]),
        )


class SaveTransactionExpirationButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that save transaction expiration button was pressed."""

    def __init__(self) -> None:
        super().__init__("Save", variant="success")


class TransactionExpiration(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]
    BIG_TITLE = "Settings"
    SUBTITLE = "Transaction expiration"
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def create_main_panel(self) -> ComposeResult:
        current_shorthand = timedelta_to_shorthand_timedelta(self.profile.transaction_expiration)
        with SectionScrollable("Set transaction expiration", focusable=True):
            yield CurrentTransactionExpiration(current_shorthand)
            yield TransactionExpirationInput(current_shorthand)
            yield SaveTransactionExpirationButton()

    @on(SaveTransactionExpirationButton.Pressed)
    @on(CliveInput.Submitted)
    def save_transaction_expiration(self) -> None:
        expiration_input = self.query_exactly_one(TransactionExpirationInput)

        if not expiration_input.validate_passed():
            return

        new_value = shorthand_timedelta_to_timedelta(expiration_input.value_or_error)
        self.profile.set_transaction_expiration(new_value)

        new_shorthand = timedelta_to_shorthand_timedelta(new_value)
        self.app.trigger_profile_watchers()
        self.notify(f"Transaction expiration set to {new_shorthand}.")
        self.app.pop_screen()

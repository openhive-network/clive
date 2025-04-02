from __future__ import annotations

from typing import Final

from textual import on

from clive.__private.core.constants.tui.placeholders import KNOWN_EXCHANGE_MEMO_PLACEHOLDER
from clive.__private.models import Asset
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.liquid_asset_amount_input import LiquidAssetAmountInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive.__private.ui.widgets.inputs.receiver_input import ReceiverInput


class KnownExchangeHandler(CliveWidget):
    """
    A handler for known exchange accounts.

    The widget responds to messages: `KnownExchangeDetected` and `KnownExchangeGone` emitted by KnownExchangeInput`.
    Automatically disables/enables the selector  from `LiquidAssetAmountInput` and makes memo input required.

    Notice
    ______

    For the handler to work properly, you must also use `KnownExchangeInput`!
    Handler is designed to be used as a context manager, and the input must be placed under
    the with statement with the handler.
    """

    DEFAULT_CSS = """
    KnownExchangeHandler {
        height: auto;
    }
    """
    MEMO_REQUIRED_VALIDATION_MESSAGE: Final[str] = "Memo is required by the known exchange account!"

    def __init__(self) -> None:
        super().__init__()

        self._previous_memo_placeholder = ""
        self._previous_memo_required = False
        self._previous_memo_always_show_title = False

    @property
    def memo_input(self) -> MemoInput:
        return self.query_exactly_one(MemoInput)

    def on_mount(self) -> None:
        self._update_previous_state()

    @on(ReceiverInput.KnownExchangeDetected)
    def set_known_exchange_mode(self) -> None:
        self._update_previous_state()
        self._change_selector_state(disable=True)
        self._change_memo_requirement(required=True)

    @on(ReceiverInput.KnownExchangeGone)
    def unset_known_exchange_mode(self) -> None:
        self._change_selector_state(disable=False)
        self._change_memo_requirement(required=False)

    def _update_previous_state(self) -> None:
        memo_input = self.memo_input.input
        self._previous_memo_placeholder = memo_input.unmodified_placeholder
        self._previous_memo_required = memo_input.required
        self._previous_memo_always_show_title = memo_input.always_show_title

    def _change_selector_state(self, *, disable: bool) -> None:
        """Disables/enables the selector from `LiquidAssetAmountInput`."""
        amount_input = self.query_exactly_one(LiquidAssetAmountInput)

        if disable:
            amount_input.disable_currency_selector()
        else:
            amount_input.enable_currency_selector()

        if disable and amount_input.selected_asset_type is not Asset.Hive:
            amount_input.select_asset(Asset.Hive)

    def _change_memo_requirement(self, *, required: bool) -> None:
        """Make memo input required or optional."""
        memo_input = self.memo_input

        if required:
            memo_input.input.always_show_title = True
            self._modify_placeholder(memo_input, required=required)
            memo_input.make_required(message=self.MEMO_REQUIRED_VALIDATION_MESSAGE)
            return

        memo_input.input.always_show_title = self._previous_memo_always_show_title
        self._modify_placeholder(memo_input, required=self._previous_memo_required)
        memo_input.make_required() if self._previous_memo_required else memo_input.make_optional()

    def _modify_placeholder(self, memo_input: MemoInput, *, required: bool) -> None:
        if required:
            memo_input.input.placeholder = KNOWN_EXCHANGE_MEMO_PLACEHOLDER
            return

        memo_input.input.placeholder = self._previous_memo_placeholder

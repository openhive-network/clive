from __future__ import annotations

from textual import on

from clive.__private.models import Asset
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.known_exchange_input import KnownExchangeInput
from clive.__private.ui.widgets.inputs.liquid_asset_amount_input import LiquidAssetAmountInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput


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

    @on(KnownExchangeInput.KnownExchangeDetected)
    def set_known_exchange_mode(self) -> None:
        self._change_selector_state(disable=True)
        self._change_memo_requirement(required=True)

    @on(KnownExchangeInput.KnownExchangeGone)
    def unset_known_exchange_mode(self) -> None:
        self._change_selector_state(disable=False)
        self._change_memo_requirement(required=False)

    def _change_selector_state(self, *, disable: bool) -> None:
        """Disables/enables the selector from `LiquidAssetAmountInput`."""
        amount_input = self.query_one(LiquidAssetAmountInput)

        if disable:
            amount_input.disable_currency_selector()
        else:
            amount_input.enable_currency_selector()

        if disable and amount_input.selected_asset_type is not Asset.Hive:
            amount_input.select_asset(Asset.Hive)

    def _change_memo_requirement(self, *, required: bool) -> None:
        """Make memo input required or optional."""
        memo_input = self.query_one(MemoInput)

        self._modify_placeholder(memo_input, required=required)

        if required:
            # This won't work correctly when the memo was required BEFORE the exchange is detected
            # because we make it always optional when exchange is gone.
            # It means we do not preserve the original state after the exchange is gone.
            assert not memo_input.input.required, f"Shouldn't use {type(self)} with required memo input!"
            memo_input.input.always_show_title = True
            memo_input.make_required(message="Memo is required by the known exchange account!")
            return

        memo_input.input.always_show_title = False
        memo_input.make_optional()

    def _modify_placeholder(self, memo_input: MemoInput, *, required: bool) -> None:
        if required:
            memo_input.input.placeholder = "Check your memo on the known exchange account!"
            return

        memo_input.input.set_placeholder_to_unmodified()

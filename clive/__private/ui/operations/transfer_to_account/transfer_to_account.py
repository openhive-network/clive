from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.bindings import OperationActionBindings
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.liquid_asset_amount_input import LiquidAssetAmountInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive.models import Asset
from clive.models.asset import AssetAmount
from schemas.operations import TransferOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


LiquidAssetCallableT = Callable[[AssetAmount], Asset.LiquidT]


class ScrollablePart(ScrollableContainer, can_focus=False):
    """All the scrollable content of the screen."""


class Body(Grid):
    """All the content of the screen, excluding the title."""


class TransferToAccount(OperationBaseScreen, OperationActionBindings):
    CSS_PATH = [
        *OperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        self._to_input = AccountNameInput("To")
        self._amount_input = LiquidAssetAmountInput()
        self._memo_input = MemoInput(include_title_in_placeholder_when_blurred=True)

    @property
    def from_account(self) -> str:
        return self.app.world.profile_data.working_account.name

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Transfer to account")
        with ScrollablePart(), Body():
            yield AccountNameInput(
                "From",
                self.from_account,
                always_show_title=True,
                required=False,
                ask_known_account=False,
                disabled=True,
            )
            yield self._to_input
            yield self._amount_input
            yield self._memo_input

    def _create_operation(self) -> TransferOperation | None:
        # So all inputs are validated together, and not one by one.
        if not CliveValidatedInput.validate_many(self._to_input, self._amount_input, self._memo_input):
            return None

        return TransferOperation(
            from_=self.from_account,
            to=self._to_input.value_or_error,
            amount=self._amount_input.value_or_error,
            memo=self._memo_input.value_or_error,
        )

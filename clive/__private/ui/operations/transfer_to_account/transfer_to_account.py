from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from textual.containers import Grid

from clive.__private.models import Asset
from clive.__private.models.aliased import TransferOperation
from clive.__private.models.asset import AssetAmount
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.bindings import OperationActionBindings
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput
from clive.__private.ui.widgets.inputs.liquid_asset_amount_input import LiquidAssetAmountInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive.__private.ui.widgets.section import SectionScrollable

if TYPE_CHECKING:
    from textual.app import ComposeResult


LiquidAssetCallableT = Callable[[AssetAmount], Asset.LiquidT]


class Body(Grid):
    """All the content of the screen, excluding the title."""


class TransferToAccount(OperationBaseScreen, OperationActionBindings):
    CSS_PATH = [
        *OperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self, *, default_asset_selected: type[Asset.LiquidT] = Asset.Hbd) -> None:
        super().__init__()

        self._to_input = AccountNameInput("To")
        self._amount_input = LiquidAssetAmountInput()
        self._memo_input = MemoInput(include_title_in_placeholder_when_blurred=True)
        self._default_asset_selected = default_asset_selected

    def on_mount(self) -> None:
        self._amount_input.select_asset(self._default_asset_selected)
        self._to_input.clear_validation()

    @property
    def from_account(self) -> str:
        return self.profile.accounts.working.name

    def create_left_panel(self) -> ComposeResult:
        with SectionScrollable("Perform a transfer to account"), Body():
            yield LabelizedInput("From", self.from_account)
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

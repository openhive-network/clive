from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.currency_selector_liquid import CurrencySelectorLiquid
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import TransferToSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class TransferToSavings(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__to_input = Input(placeholder="e.g.: some-account")
        self.__amount_input = Input(placeholder="e.g.: 5.000")
        self.__memo_input = Input(placeholder="e.g.: For the coffee!")
        self.__currency_selector = CurrencySelectorLiquid()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer to savings")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="from-label")
                yield PlaceTaker()
                yield Static("to", classes="label")
                yield self.__to_input
                yield Static("amount", classes="label")
                yield self.__amount_input
                yield self.__currency_selector
                yield Static("memo", classes="label")
                yield self.__memo_input

    def _create_operation(self) -> Operation | None:
        return TransferToSavingsOperation(
            from_=str(self.app.world.profile_data.working_account.name),
            to=self.__to_input.value,
            amount=self.__currency_selector.selected.value(float(self.__amount_input.value)),
            memo=self.__memo_input.value,
        )

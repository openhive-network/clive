from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.currency_selector_liquid import CurrencySelectorLiquid
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset, Operation
from schemas.operations import FeedPublishOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class ExchangeRateTaker(Static):
    """Container used for making correct layout of exchange rate"""


class FeedPublish(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__base_input = Input(placeholder="e.g: 1")
        self.__quote_input = Input(placeholder="e.g: 10")
        self.__currency_selector_base = CurrencySelectorLiquid()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Feed publish")
            with Body():
                yield Static("publisher", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="publisher-label")
                yield ExchangeRateTaker()
                yield BigTitle("Exchange rate")
                yield PlaceTaker()
                yield Static("base", classes="label")
                yield self.__base_input
                yield self.__currency_selector_base
                yield Static("quote", classes="label")
                yield self.__quote_input

    def _create_operation(self) -> Operation | None:
        exchange_rate = {
            "base": self.__currency_selector_base.selected.value(float(self.__base_input.value)),
            "quote": Asset.hive(float(self.__quote_input.value)),
        }

        return FeedPublishOperation(
            publisher=str(self.app.world.profile_data.name),
            exchange_rate=exchange_rate,
        )

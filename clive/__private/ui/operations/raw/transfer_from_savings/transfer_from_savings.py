from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.currency_selector import CurrencySelectorLiquid
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.placeholders_constants import (
    ACCOUNT_NAME_PLACEHOLDER,
    ASSET_AMOUNT_PLACEHOLDER,
    ID_PLACEHOLDER,
    MEMO_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import TransferFromSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Asset


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class TransferFromSavings(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_request_id = str(get_default_from_model(TransferFromSavingsOperation, "request_id", int))

        self.__to_input = Input(placeholder=ACCOUNT_NAME_PLACEHOLDER)
        self.__request_id_input = Input(default_request_id, placeholder=ID_PLACEHOLDER)
        self.__amount_input = Input(placeholder=ASSET_AMOUNT_PLACEHOLDER)
        self.__memo_input = Input(placeholder=MEMO_PLACEHOLDER)
        self.__currency_selector = CurrencySelectorLiquid()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Transfer from savings")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield PlaceTaker()
                yield Static("to", classes="label")
                yield self.__to_input
                yield PlaceTaker()
                yield Static("request id", classes="label")
                yield self.__request_id_input
                yield PlaceTaker()
                yield Static("amount", classes="label")
                yield self.__amount_input
                yield self.__currency_selector
                yield Static("memo", classes="label")
                yield self.__memo_input

    def _create_operation(self) -> TransferFromSavingsOperation[Asset.Hive, Asset.Hbd]:
        return TransferFromSavingsOperation(
            from_=self.app.world.profile_data.working_account.name,
            to=self.__to_input.value,
            request_id=int(self.__request_id_input.value),
            amount=self.__currency_selector.selected.value(self.__amount_input.value),
            memo=self.__memo_input.value,
        )

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
    ACCOUNT_NAME2_PLACEHOLDER,
    ACCOUNT_NAME_PLACEHOLDER,
    ASSET_AMOUNT_PLACEHOLDER,
    DATE_PLACEHOLDER,
    ID_PLACEHOLDER,
    JSON_DATA_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import EscrowTransferOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class AdditionalPlaceTaker(Static):
    """Additional container for making correct layout for Inputs, except fee."""


class EscrowTransfer(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_escrow_id = str(get_default_from_model(EscrowTransferOperation, "escrow_id", int))

        self.__to_input = Input(placeholder=ACCOUNT_NAME_PLACEHOLDER)
        self.__agent_input = Input(placeholder=ACCOUNT_NAME2_PLACEHOLDER)
        self.__escrow_id_input = Input(default_escrow_id, placeholder=ID_PLACEHOLDER)
        self.__hbd_amount_input = Input(placeholder="Notice: if don't want to use, leave 0.000 here", value="0.000")
        self.__hive_amount_input = Input(placeholder="Notice: if don't want to use, leave 0.000 here", value="0.000")
        self.__fee_input = Input(placeholder=ASSET_AMOUNT_PLACEHOLDER)
        self.__ratification_deadline_input = Input(placeholder=DATE_PLACEHOLDER)
        self.__escrow_expiration_input = Input(placeholder=DATE_PLACEHOLDER)
        self.__json_meta_input = Input(placeholder=JSON_DATA_PLACEHOLDER)
        self.__currency_selector = CurrencySelectorLiquid()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Escrow transfer")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="from-label")
                yield AdditionalPlaceTaker()
                yield Static("to", classes="label")
                yield self.__to_input
                yield Static("agent", classes="label")
                yield self.__agent_input
                yield Static("escrow id", classes="label")
                yield self.__escrow_id_input
                yield Static("hbd amount", classes="label")
                yield self.__hbd_amount_input
                yield Static("hive amount", classes="label")
                yield self.__hive_amount_input
                yield Static("ratification deadline", classes="label")
                yield self.__ratification_deadline_input
                yield Static("escrow expiration", classes="label")
                yield self.__escrow_expiration_input
                yield Static("json meta", classes="label")
                yield self.__json_meta_input
                yield PlaceTaker()
                yield Static("fee", classes="label")
                yield self.__fee_input
                yield self.__currency_selector

    def _create_operation(self) -> EscrowTransferOperation[Asset.Hive, Asset.Hbd]:
        return EscrowTransferOperation(
            from_=self.app.world.profile_data.name,
            to=self.__to_input.value,
            agent=self.__agent_input.value,
            escrow_id=int(self.__escrow_id_input.value),
            hbd_amount=Asset.hbd(self.__hbd_amount_input.value),
            hive_amount=Asset.hive(self.__hive_amount_input.value),
            ratification_deadline=self.__ratification_deadline_input.value,
            escrow_expiration=self.__ratification_deadline_input.value,
            json_meta=self.__json_meta_input.value,
            fee=self.__currency_selector.create_asset(self.__fee_input.value),
        )

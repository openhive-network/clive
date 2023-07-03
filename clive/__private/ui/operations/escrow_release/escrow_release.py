from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import EscrowReleaseOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from schemas.__private.hive_fields_basic_schemas import AssetHbdHF26, AssetHiveHF26


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid"""


class EscrowRelease(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        str(get_default_from_model(EscrowReleaseOperation, "escrow_id"))

        self.__to_input = Input(placeholder="e.g: bob")
        self.__agent_input = Input(placeholder="e.g: charlie")
        self.__who_input = Input(placeholder="e.g: charlie")
        self.__receiver_input = Input(placeholder="e.g: bob")
        self.__escrow_id_input = Input(placeholder="e.g.: 23456789. Notice - default is 30")
        self.__hbd_amount_input = Input(placeholder="Notice: if don't want to use, leave 0.000 here", value="0.000")
        self.__hive_amount_input = Input(placeholder="Notice: if don't want to use, leave 0.000 here", value="0.000")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Escrow release")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="from-label")
                yield PlaceTaker()
                yield Static("to", classes="label")
                yield self.__to_input
                yield Static("agent", classes="label")
                yield self.__agent_input
                yield Static("who", classes="label")
                yield self.__who_input
                yield Static("receiver", classes="label")
                yield self.__receiver_input
                yield Static("escrow id", classes="label")
                yield self.__escrow_id_input
                yield Static("hbd amount", classes="label")
                yield self.__hbd_amount_input
                yield Static("hive amount", classes="label")
                yield self.__hive_amount_input

    def _create_operation(self) -> EscrowReleaseOperation[AssetHiveHF26, AssetHbdHF26]:
        return EscrowReleaseOperation(
            from_=str(self.app.world.profile_data.name),
            to=self.__to_input.value,
            agent=self.__agent_input.value,
            escrow_id=int(self.__escrow_id_input.value),
            hbd_amount=Asset.hbd(float(self.__hbd_amount_input.value)),
            hive_amount=Asset.hive(float(self.__hive_amount_input.value)),
            receiver=self.__receiver_input.value,
            who=self.__who_input.value,
        )

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
from schemas.operations import ConvertOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from schemas.__private.hive_fields_basic_schemas import AssetHbdHF26


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class Convert(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        default_request_id = str(get_default_from_model(ConvertOperation, "request_id"))

        self.__request_id_input = Input(default_request_id, placeholder="e.g.: 1467592156.")
        self.__amount_input = Input(placeholder="e.g.: 5.000")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Convert")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="from-label")
                yield PlaceTaker()
                yield Static("request_id", classes="label")
                yield self.__request_id_input
                yield Static("amount", classes="label")
                yield self.__amount_input

    def _create_operation(self) -> ConvertOperation[AssetHbdHF26]:
        return ConvertOperation(
            from_=str(self.app.world.profile_data.working_account.name),
            request_id=int(self.__request_id_input.value),
            amount=Asset.hbd(float(self.__amount_input.value)),
        )

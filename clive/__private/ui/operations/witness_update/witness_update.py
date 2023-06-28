from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset, Operation
from schemas.operations import WitnessUpdateOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class WitnessUpdate(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__url_input = Input(placeholder="e.g: witness-category/my-witness")
        self.__block_signing_key_input = Input(placeholder="e.g: STM8LoQjQqJHvotqBo7HjnqmUbFW9oJ2theyqonzUd9DdJ7YYHsvD")
        self.__account_creation_fee_input = Input(placeholder="account creation fee, e.g: 1.000")
        self.__maximum_block_size_input = Input(value="131072", placeholder="maximum block size")
        self.__hbd_interest_rate_input = Input(value="1000", placeholder="hbd interest rate")
        self.__fee_input = Input(placeholder="e.g: 1.000")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Witness update")
            with Body():
                yield Static("owner", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="owner-label")
                yield Static("url", classes="label")
                yield self.__url_input
                yield Static("block signing key", classes="label")
                yield self.__block_signing_key_input
                yield Static("fee", classes="label")
                yield self.__fee_input
                yield BigTitle("Props")
                yield PlaceTaker()
                yield Static("account creation fee", classes="label")
                yield self.__account_creation_fee_input
                yield Static("maximum block size", classes="label")
                yield self.__maximum_block_size_input
                yield Static("hbd interest rate", classes="label")
                yield self.__hbd_interest_rate_input

    def _create_operation(self) -> Operation | None:
        props_field = {
            "account_creation_fee": Asset.hive(float(self.__account_creation_fee_input.value)),
            "maximum_block_size": int(self.__maximum_block_size_input.value),
            "hbd_interest_rate": int(self.__hbd_interest_rate_input.value),
        }

        return WitnessUpdateOperation(
            owner=str(self.app.world.profile_data.name),
            url=self.__url_input.value,
            block_signing_key=self.__block_signing_key_input.value,
            props=props_field,
            fee=Asset.hive(float(self.__fee_input.value)),
        )

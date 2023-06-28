from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset, Operation
from schemas.operations import CreateProposalOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class CreateProposal(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__receiver_input = Input(placeholder="e.g: alice")
        self.__start_date_input = Input(placeholder="e.g: 2019-08-26T11:22:39")
        self.__end_date_input = Input(placeholder="e.g: 2019-08-27T11:22:39")
        self.__daily_pay_input = Input(placeholder="e.g: 1.000. Notice: pay in HBD")
        self.__subject_input = Input(placeholder="e.g: example subject")
        self.__permlink_input = Input(placeholder="e.g: a-post-by-alice")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Create proposal")
            with Body():
                yield Static("creator", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="creator-label")
                yield Static("receiver", classes="label")
                yield self.__receiver_input
                yield Static("start date", classes="label")
                yield self.__start_date_input
                yield Static("end date", classes="label")
                yield self.__end_date_input
                yield Static("daily pay", classes="label")
                yield self.__daily_pay_input
                yield Static("subject", classes="label")
                yield self.__subject_input
                yield Static("permlink", classes="label")
                yield self.__permlink_input

    def _create_operation(self) -> Operation | None:
        return CreateProposalOperation(
            creator=str(self.app.world.profile_data.name),
            receiver=self.__receiver_input.value,
            start_date=self.__start_date_input.value,
            end_date=self.__end_date_input.value,
            daily_pay=Asset.hbd(float(self.__daily_pay_input.value)),
            subject=self.__subject_input.value,
            permlink=self.__permlink_input.value,
        )

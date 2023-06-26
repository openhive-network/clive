from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError
from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset, Operation
from schemas.operations import CommentOptionsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class CommentOptions(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__permlink_input = Input(placeholder="e.g: a-post-by-alice")
        self.__max_accepted_payout_input = Input(placeholder="e.g: 1.000")
        self.__percent_hbd_input = Input(placeholder="e.g: 50. Notice: default value is 100")
        self.__allow_votes_input = Input(value="True")
        self.__allow_curation_rewards_input = Input(value="True")
        self.__extensions_input = Input(placeholder="e.g: []")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Comment options")
            with Body():
                yield Static("author", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="author-label")
                yield Static("permlink", classes="label")
                yield self.__permlink_input
                yield Static("max accepted payout", classes="label")
                yield self.__max_accepted_payout_input
                yield Static("percent hbd", classes="label")
                yield self.__percent_hbd_input
                yield Static("allow votes", classes="label")
                yield self.__allow_votes_input
                yield Static("allow curation rewards", classes="label")
                yield self.__allow_curation_rewards_input
                yield Static("extensions", classes="label")
                yield self.__extensions_input

    def create_operation(self) -> Operation | None:
        try:
            if self.__percent_hbd_input.value:
                return CommentOptionsOperation(
                    author=str(self.app.world.profile_data.name),
                    permlink=self.__permlink_input.value,
                    max_accepted_payout=Asset.hbd(float(self.__max_accepted_payout_input.value)),
                    percent_hbd=int(self.__percent_hbd_input.value),
                    allow_votes=bool(self.__allow_votes_input.value),
                    allow_curation_rewards=bool(self.__allow_curation_rewards_input.value),
                    extensions=self.__extensions_input.value,
                )
            return CommentOptionsOperation(  # noqa: TRY300
                author=str(self.app.world.profile_data.name),
                permlink=self.__permlink_input.value,
                max_accepted_payout=Asset.hbd(float(self.__max_accepted_payout_input.value)),
                allow_votes=bool(self.__allow_votes_input.value),
                allow_curation_rewards=bool(self.__allow_curation_rewards_input.value),
                extensions=self.__extensions_input.value,
            )
        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None

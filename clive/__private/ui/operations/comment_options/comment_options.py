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
from schemas.operations import CommentOptionsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from schemas.__private.hive_fields_basic_schemas import AssetHbdHF26


class Body(Grid):
    """All the content of the screen, excluding the title."""


class CommentOptions(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        default_percent_hbd = str(get_default_from_model(CommentOptionsOperation, "percent_hbd"))
        default_allow_votes = str(get_default_from_model(CommentOptionsOperation, "allow_votes"))
        default_allow_curation_rewards = str(get_default_from_model(CommentOptionsOperation, "allow_curation_rewards"))

        self.__permlink_input = Input(placeholder="e.g: a-post-by-alice")
        self.__max_accepted_payout_input = Input(placeholder="e.g: 1.000")
        self.__percent_hbd_input = Input(default_percent_hbd, placeholder="e.g: 50. Notice: default value is 100")
        self.__allow_votes_input = Input(default_allow_votes, placeholder="e.g: False")
        self.__allow_curation_rewards_input = Input(default_allow_curation_rewards, placeholder="e.g: False")
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

    def _create_operation(self) -> CommentOptionsOperation[AssetHbdHF26]:
        return CommentOptionsOperation(
            author=str(self.app.world.profile_data.name),
            permlink=self.__permlink_input.value,
            max_accepted_payout=Asset.hbd(float(self.__max_accepted_payout_input.value)),
            percent_hbd=int(self.__percent_hbd_input.value),
            allow_votes=bool(self.__allow_votes_input.value),
            allow_curation_rewards=bool(self.__allow_curation_rewards_input.value),
            extensions=self.__extensions_input.value,
        )

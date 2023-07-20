from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.placeholders_constants import (
    ACCOUNT_NAME_PLACEHOLDER,
    ID_PLACEHOLDER,
    PERMLINK_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import VoteOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class Vote(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_weight = str(get_default_from_model(VoteOperation, "weight", int))

        self.__author_input = Input(placeholder=ACCOUNT_NAME_PLACEHOLDER)
        self.__permlink_input = Input(placeholder=PERMLINK_PLACEHOLDER)
        self.__weight_input = Input(default_weight, placeholder=ID_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Vote")
            with Body():
                yield Static("voter", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="voter-label")
                yield PlaceTaker()
                yield Static("author", classes="label")
                yield self.__author_input
                yield Static("permlink", classes="label")
                yield self.__permlink_input
                yield Static("weight", classes="label")
                yield self.__weight_input

    def _create_operation(self) -> VoteOperation:
        return VoteOperation(
            voter=self.app.world.profile_data.working_account.name,
            author=self.__author_input.value,
            permlink=self.__permlink_input.value,
            weight=int(self.__weight_input.value),
        )

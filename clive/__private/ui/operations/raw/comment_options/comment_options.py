from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Checkbox

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput
from clive.__private.ui.widgets.inputs.permlink_input import PermlinkInput
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import (
    PERCENT_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import CommentOptionsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class CommentOptions(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        default_percent_hbd = get_default_from_model(CommentOptionsOperation, "percent_hbd", int)
        default_allow_votes = get_default_from_model(CommentOptionsOperation, "allow_votes", bool)
        default_allow_curation_rewards = get_default_from_model(CommentOptionsOperation, "allow_curation_rewards", bool)

        self.__permlink_input = PermlinkInput()
        self.__max_accepted_payout_input = NumericInput(label="max accepted payout")
        self.__percent_hbd_input = IntegerInput(
            label="percent hbd", value=default_percent_hbd, placeholder=PERCENT_PLACEHOLDER
        )
        self.__allow_votes_input = Checkbox("allow votes", value=default_allow_votes)
        self.__allow_curation_rewards_input = Checkbox("allow curation reward", value=default_allow_curation_rewards)
        self.__extensions_input = TextInput(label="extensions", placeholder="e.g: []")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Comment options")
            with ScrollableContainer(), Body():
                yield InputLabel("author")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="author-label")
                yield from self.__permlink_input.compose()
                yield from self.__max_accepted_payout_input.compose()
                yield from self.__percent_hbd_input.compose()
                yield from self.__extensions_input.compose()
                yield self.__allow_votes_input
                yield self.__allow_curation_rewards_input

    def _create_operation(self) -> CommentOptionsOperation | None:
        max_accepted_payout = self.__max_accepted_payout_input.value
        percent_hbd = self.__percent_hbd_input.value
        extensions = self.__extensions_input.value

        if not max_accepted_payout or not percent_hbd or not extensions:
            return None

        return CommentOptionsOperation(
            author=self.app.world.profile_data.name,
            permlink=self.__permlink_input.value,
            max_accepted_payout=Asset.hbd(max_accepted_payout),
            percent_hbd=percent_hbd,
            allow_votes=self.__allow_votes_input.value,
            allow_curation_rewards=self.__allow_curation_rewards_input.value,
            extensions=extensions,
        )

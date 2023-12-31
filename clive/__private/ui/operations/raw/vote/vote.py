from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.permlink_input import PermlinkInput
from clive.__private.ui.widgets.placeholders_constants import (
    ID_PLACEHOLDER,
)
from schemas.operations import VoteOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class Vote(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        default_weight = get_default_from_model(VoteOperation, "weight", int)

        self.__author_input = AccountNameInput(label="author")
        self.__permlink_input = PermlinkInput()
        self.__weight_input = IntegerInput(label="weight", value=default_weight, placeholder=ID_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Vote")
        with ScrollableContainer(), Body():
            yield InputLabel("voter")
            yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="voter-label")
            yield from self.__author_input.compose()
            yield from self.__permlink_input.compose()
            yield from self.__weight_input.compose()

    def _create_operation(self) -> VoteOperation | None:
        weight = self.__weight_input.value
        if not weight:
            return None

        return VoteOperation(
            voter=self.app.world.profile_data.working_account.name,
            author=self.__author_input.value,
            permlink=self.__permlink_input.value,
            weight=weight,
        )

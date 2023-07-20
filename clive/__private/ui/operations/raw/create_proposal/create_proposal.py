from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.placeholders_constants import (
    ACCOUNT_NAME_PLACEHOLDER,
    ASSET_AMOUNT_PLACEHOLDER,
    DATE_PLACEHOLDER,
    PERMLINK_PLACEHOLDER,
)
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import CreateProposalOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class CreateProposal(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__receiver_input = Input(placeholder=ACCOUNT_NAME_PLACEHOLDER)
        self.__start_date_input = Input(placeholder=DATE_PLACEHOLDER)
        self.__end_date_input = Input(placeholder=DATE_PLACEHOLDER)
        self.__daily_pay_input = Input(placeholder=ASSET_AMOUNT_PLACEHOLDER)
        self.__subject_input = Input(placeholder="e.g: example subject")
        self.__permlink_input = Input(placeholder=PERMLINK_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Create proposal")
            with Body():
                yield Static("creator", classes="label")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="creator-label")
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

    def _create_operation(self) -> CreateProposalOperation[Asset.Hbd]:
        return CreateProposalOperation(
            creator=self.app.world.profile_data.name,
            receiver=self.__receiver_input.value,
            start_date=self.__start_date_input.value,
            end_date=self.__end_date_input.value,
            daily_pay=Asset.hbd(self.__daily_pay_input.value),
            subject=self.__subject_input.value,
            permlink=self.__permlink_input.value,
        )

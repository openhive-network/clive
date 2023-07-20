from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_NAME_PLACEHOLDER, ASSET_AMOUNT_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import ClaimAccountOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class ClaimAccount(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__creator_input = Input(placeholder=ACCOUNT_NAME_PLACEHOLDER)
        self.__fee_input = Input(placeholder=f"{ASSET_AMOUNT_PLACEHOLDER} Notice: if you want to pay in RC type 0")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Claim account")
            with Body():
                yield Static("creator", classes="label")
                yield self.__creator_input
                yield Static("fee", classes="label")
                yield self.__fee_input

    def _create_operation(self) -> ClaimAccountOperation[Asset.Hive]:
        return ClaimAccountOperation(creator=self.__creator_input.value, fee=Asset.hive(self.__fee_input.value))

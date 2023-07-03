from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import WitnessBlockApproveOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class WitnessBlockApprove(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__witness_input = Input(placeholder="e.g.: hiveio")
        self.__block_id_input = Input(placeholder="e.g.: 10000")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Witness block approve")
            with Body():
                yield Static("witness", classes="label")
                yield self.__witness_input
                yield Static("block_id", classes="label")
                yield self.__block_id_input

    def _create_operation(self) -> WitnessBlockApproveOperation:
        return WitnessBlockApproveOperation(witness=self.__witness_input.value, block_id=self.__block_id_input.value)

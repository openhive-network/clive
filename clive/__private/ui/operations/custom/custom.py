from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import CustomOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class Custom(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__required_auths_input = Input(placeholder="e.g.: alice,bob,charlie")
        self.__id_input = Input(value="0")
        self.__data_input = Input(placeholder="Custom data input")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Custom")
            with Body():
                yield Static("required auths", classes="label")
                yield self.__required_auths_input
                yield Static("id", classes="label")
                yield self.__id_input
                yield Static("data", classes="label")
                yield self.__data_input

    def _create_operation(self) -> CustomOperation:
        required_auths_in_list = self.__required_auths_input.value.split(",")
        required_auths_in_list = [x.strip(" ") for x in required_auths_in_list]

        return CustomOperation(
            required_auths=required_auths_in_list,
            id_=int(self.__id_input.value),
            data=[self.__data_input.value],
        )

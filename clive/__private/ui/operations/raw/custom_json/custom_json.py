from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.inputs.id_input import IdInput, IdT
from clive.__private.ui.widgets.inputs.json_data_input import JsonDataInput
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import CustomJsonOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class CustomJson(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__required_auths_input = CustomInput(label="required auths", placeholder="e.g.: alice,bob,charlie")
        self.__required_posting_auths_input = CustomInput(
            label="required posting auths", placeholder="e.g: alice,bob,charlie"
        )
        self.__id_input = IdInput[IdT](value=0)
        self.__json_input = JsonDataInput(label="json")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Custom json")
            with ScrollableContainer(), Body():
                yield from self.__required_auths_input.compose()
                yield from self.__required_posting_auths_input.compose()
                yield from self.__id_input.compose()
                yield from self.__json_input.compose()

    def _create_operation(self) -> CustomJsonOperation:
        required_auths_in_list = self.__required_auths_input.value.split(",")
        required_auths_in_list = [x.strip(" ") for x in required_auths_in_list]

        required_posting_auths_in_list = self.__required_posting_auths_input.value.split(",")
        required_posting_auths_in_list = [x.strip(" ") for x in required_posting_auths_in_list]
        return CustomJsonOperation(
            required_auths=required_auths_in_list,
            required_posting_auths=required_posting_auths_in_list,
            id_=int(self.__id_input.value),
            json_=self.__json_input.value,
        )

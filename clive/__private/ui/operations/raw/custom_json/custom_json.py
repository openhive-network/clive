from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.id_input import IdInput
from clive.__private.ui.widgets.inputs.json_data_input import JsonDataInput
from clive.__private.ui.widgets.inputs.text_input import TextInput
from schemas.operations import CustomJsonOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class CustomJson(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__required_auths_input = TextInput(label="required auths", placeholder="e.g.: alice,bob,charlie")
        self.__required_posting_auths_input = TextInput(
            label="required posting auths", placeholder="e.g: alice,bob,charlie"
        )
        self.__id_input = IdInput(value=0)
        self.__json_input = JsonDataInput(label="json")

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Custom json")
        with ScrollableContainer(), Body():
            yield from self.__required_auths_input.compose()
            yield from self.__required_posting_auths_input.compose()
            yield from self.__id_input.compose()
            yield from self.__json_input.compose()

    def _create_operation(self) -> CustomJsonOperation | None:
        required_auths_in_list = self.__required_auths_input.value.split(",")
        required_auths_in_list = [x.strip(" ") for x in required_auths_in_list]

        required_posting_auths_in_list = self.__required_posting_auths_input.value.split(",")
        required_posting_auths_in_list = [x.strip(" ") for x in required_posting_auths_in_list]

        id_value = self.__id_input.value
        if not id_value:
            return None

        return CustomJsonOperation(
            required_auths=required_auths_in_list,
            required_posting_auths=required_posting_auths_in_list,
            id_=id_value,
            json_=self.__json_input.value,
        )

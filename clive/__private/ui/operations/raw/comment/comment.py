from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.json_data_input import JsonDataInput
from clive.__private.ui.widgets.inputs.permlink_input import PermlinkInput
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import ACCOUNT_NAME2_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import CommentOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class Comment(RawOperationBaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self) -> None:
        super().__init__()

        self.__parent_author_input = AccountNameInput(label="parent  author")
        self.__parent_permlink_input = PermlinkInput(label="parent permlink")
        self.__author_input = AccountNameInput(label="author", placeholder=ACCOUNT_NAME2_PLACEHOLDER)
        self.__permlink_input = PermlinkInput()
        self.__title_input = TextInput(label="title", placeholder="e.g: A post by bob")
        self.__body_input = TextInput(label="body", placeholder="e.g: Look at my awesome post")
        self.__json_metadata_input = JsonDataInput()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Comment")
            with ScrollableContainer(), Body():
                yield from self.__author_input.compose()
                yield from self.__permlink_input.compose()
                yield from self.__title_input.compose()
                yield from self.__body_input.compose()
                yield from self.__parent_author_input.compose()
                yield from self.__parent_permlink_input.compose()
                yield from self.__json_metadata_input.compose()

    def _create_operation(self) -> CommentOperation:
        return CommentOperation(
            author=self.__author_input.value,
            permlink=self.__permlink_input.value,
            title=self.__title_input.value,
            body=self.__body_input.value,
            parent_author=self.__parent_author_input.value,
            parent_permlink=self.__parent_permlink_input.value,
            json_metadata=self.__json_metadata_input.value,
        )

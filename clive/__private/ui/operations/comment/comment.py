from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import CommentOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class Comment(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__parent_author_input = Input(placeholder="e.g: alice. Notice: this field can be empty")
        self.__parent_permlink_input = Input(placeholder="e.g: a-post-by-alice")
        self.__author_input = Input(placeholder="e.g: joe")
        self.__permlink_input = Input(placeholder="e.g: a-post-by-alice")
        self.__title_input = Input(placeholder="e.g: A post by Joe")
        self.__body_input = Input(placeholder="e.g: Look at my awesome post")
        self.__json_metadata_input = Input(placeholder="e.g: {}")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Comment")
            with Body():
                yield Static("author", classes="label")
                yield self.__author_input
                yield Static("permlink", classes="label")
                yield self.__permlink_input
                yield Static("title", classes="label")
                yield self.__title_input
                yield Static("body", classes="label")
                yield self.__body_input
                yield Static("parent author", classes="label")
                yield self.__parent_author_input
                yield Static("parent permlink", classes="label")
                yield self.__parent_permlink_input
                yield Static("json metadata", classes="label")
                yield self.__json_metadata_input

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

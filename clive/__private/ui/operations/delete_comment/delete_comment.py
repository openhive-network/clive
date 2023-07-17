from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import DeleteCommentOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class DeleteComment(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__permlink_input = Input(placeholder="e.g.: a-post-by-alice")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Delete comment")
            with Body():
                yield Static("author", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="author-label")
                yield PlaceTaker()
                yield Static("permlink", classes="label")
                yield self.__permlink_input

    def _create_operation(self) -> DeleteCommentOperation:
        return DeleteCommentOperation(
            author=str(self.app.world.profile_data.name),
            permlink=self.__permlink_input.value,
        )

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.inputs.permlink_input import PermlinkInput
from schemas.operations import DeleteCommentOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class DeleteComment(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__permlink_input = PermlinkInput()

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Delete comment")
        with ScrollableContainer(), Body():
            yield InputLabel("author")
            yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="author-label")
            yield from self.__permlink_input.compose()

    def _create_operation(self) -> DeleteCommentOperation:
        return DeleteCommentOperation(
            author=self.app.world.profile_data.working_account.name,
            permlink=self.__permlink_input.value,
        )

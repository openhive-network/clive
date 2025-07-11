from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.binding import Binding
from textual.widgets import MarkdownViewer

from clive.__private.core.constants.env import ROOT_DIRECTORY
from clive.__private.ui.screens.base_screen import BaseScreen

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult


class Help(BaseScreen):
    """The help screen for the application. Created dynamically, based on previously active screen."""

    BINDINGS = [
        Binding("f1,q,question_mark,escape", "app.pop_screen", "Back", key_display="esc"),
        Binding("t", "toggle_table_of_contents", "Toggle TOC"),
    ]

    GLOBAL_HELP_FILE_PATH: Final[Path] = ROOT_DIRECTORY / "__private/ui/global_help.md"

    SHOW_RAW_HEADER = True

    @property
    def markdown_viewer(self) -> MarkdownViewer:
        """Get the Markdown widget."""
        return self.query_exactly_one(MarkdownViewer)

    def create_main_panel(self) -> ComposeResult:
        yield MarkdownViewer(show_table_of_contents=False)

    async def on_mount(self) -> None:
        await self.markdown_viewer.go(self.GLOBAL_HELP_FILE_PATH)

    def action_toggle_table_of_contents(self) -> None:
        self.markdown_viewer.show_table_of_contents = not self.markdown_viewer.show_table_of_contents

from __future__ import annotations

import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Final

from textual.binding import Binding
from textual.widgets import MarkdownViewer

from clive.__private.core.constants.env import ROOT_DIRECTORY
from clive.__private.ui.screens.base_screen import BaseScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Help(BaseScreen):
    """The help screen for the application. Created dynamically, based on previously active screen."""

    BINDINGS = [
        Binding("space,q,question_mark,escape", "app.pop_screen", "Back", key_display="esc"),
        Binding("t", "toggle_table_of_contents", "Toggle TOC"),
        Binding("ctrl+p", "back", "Back", show=False),
        Binding("ctrl+n", "forward", "Forward", show=False),
    ]

    GLOBAL_HELP_FILE_PATH: Final[Path] = ROOT_DIRECTORY / "__private/ui/global_help.md"

    def __init__(self) -> None:
        super().__init__()
        screen_file_path = Path(inspect.getfile(self.app.screen.__class__))
        screen_help_file_path = Path(f"{screen_file_path.with_suffix('')}_help.md")
        if screen_help_file_path.exists():
            self.__help_file_path = screen_help_file_path
        else:
            self.__help_file_path = self.GLOBAL_HELP_FILE_PATH

    @property
    def markdown_viewer(self) -> MarkdownViewer:
        """Get the Markdown widget."""
        return self.query_exactly_one(MarkdownViewer)

    def create_main_panel(self) -> ComposeResult:
        yield MarkdownViewer()

    async def on_mount(self) -> None:
        await self.markdown_viewer.go(self.__help_file_path)

    def action_toggle_table_of_contents(self) -> None:
        self.markdown_viewer.show_table_of_contents = not self.markdown_viewer.show_table_of_contents

    async def action_back(self) -> None:
        await self.markdown_viewer.back()

    async def action_forward(self) -> None:
        await self.markdown_viewer.forward()

from __future__ import annotations

import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Final

from textual.binding import Binding
from textual.widgets import MarkdownViewer

from clive.__private.core.constants.env import ROOT_DIRECTORY
from clive.__private.ui.create_profile.create_profile import CreateProfileWelcomeScreen
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.dashboard import Dashboard

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Help(BaseScreen):
    """The help screen for the application. Created dynamically, based on previously active screen."""

    BINDINGS = [
        Binding("space,q,question_mark,escape", "app.pop_screen", "Back", key_display="ESC"),
        Binding("t", "toggle_table_of_contents", "Toggle TOC"),
        Binding("ctrl+p", "back", "Back"),
        Binding("ctrl+n", "forward", "Forward"),
    ]

    GLOBAL_HELP_FILE_PATH: Final[Path] = ROOT_DIRECTORY / "__private/ui/global_help.md"
    HELP_NOT_FOUND_FILE_PATH: Final[Path] = ROOT_DIRECTORY / "__private/ui/help_not_found.md"

    def __init__(self) -> None:
        super().__init__()

        if isinstance(self.app.screen, Dashboard | CreateProfileWelcomeScreen):
            self.__help_file_path: Path = self.GLOBAL_HELP_FILE_PATH
        else:
            class_path = Path(inspect.getfile(self.app.screen.__class__))
            screen_help_file = class_path.parent / "help.md"
            self.__help_file_path = screen_help_file if screen_help_file.exists() else self.HELP_NOT_FOUND_FILE_PATH

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

from __future__ import annotations

import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Final

from textual.binding import Binding
from textual.widgets import MarkdownViewer

from clive.__private.core.constants.env import ROOT_DIRECTORY
from clive.__private.ui.bindings import CLIVE_PREDEFINED_BINDINGS
from clive.__private.ui.screens.base_screen import BaseScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Help(BaseScreen):
    """The help screen for the application. Created dynamically, based on previously active screen."""

    BINDINGS = [
        Binding("q,escape", "app.pop_screen", "Back", key_display="esc"),
        CLIVE_PREDEFINED_BINDINGS.help.toggle_help.create(action="app.pop_screen", description="Back", show=False),
        CLIVE_PREDEFINED_BINDINGS.help.toggle_table_of_contents.create(description="Toggle TOC"),
        CLIVE_PREDEFINED_BINDINGS.form_navigation.previous_screen.create(action="back", description="Back", show=False),
        CLIVE_PREDEFINED_BINDINGS.form_navigation.next_screen.create(
            action="forward", description="Forward", show=False
        ),
    ]

    GLOBAL_HELP_FILE_PATH: Final[Path] = ROOT_DIRECTORY / "__private/ui/global_help.md"

    SHOW_RAW_HEADER = True

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
        content = self.__help_file_path.read_text()
        new_content = self.app.custom_bindings.get_formatted_global_bindings(content)
        yield MarkdownViewer(new_content, show_table_of_contents=False)

    def action_toggle_table_of_contents(self) -> None:
        self.markdown_viewer.show_table_of_contents = not self.markdown_viewer.show_table_of_contents

    async def action_back(self) -> None:
        await self.markdown_viewer.back()

    async def action_forward(self) -> None:
        await self.markdown_viewer.forward()

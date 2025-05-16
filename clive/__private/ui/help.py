from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.binding import Binding
from textual.widgets import MarkdownViewer

from clive.__private.core.constants.env import ROOT_DIRECTORY
from clive.__private.core.constants.tui.global_bindings import HIDE_HELP
from clive.__private.core.constants.tui.navigation_bindings import NEXT_SCREEN, PREVIOUS_SCREEN
from clive.__private.ui.screens.base_screen import BaseScreen

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult


class Help(BaseScreen):
    """The help screen for the application. Created dynamically, based on previously active screen."""

    BINDINGS = [
        Binding(HIDE_HELP.key, "app.pop_screen", "Back", id=HIDE_HELP.id),
        Binding("t", "toggle_table_of_contents", "Toggle TOC"),
        Binding(PREVIOUS_SCREEN.key, "back", "Back", show=False, id=PREVIOUS_SCREEN.id),
        Binding(NEXT_SCREEN.key, "forward", "Forward", show=False, id=NEXT_SCREEN.id),
    ]

    GLOBAL_HELP_FILE_PATH: Final[Path] = ROOT_DIRECTORY / "__private/ui/global_help.md"

    SHOW_RAW_HEADER = True

    @property
    def markdown_viewer(self) -> MarkdownViewer:
        """Get the Markdown widget."""
        return self.query_exactly_one(MarkdownViewer)

    def create_main_panel(self) -> ComposeResult:
        with self.GLOBAL_HELP_FILE_PATH.open() as f:
            content = f.read()
        new_content = content.replace(
            "@GLOBAL_BINDING_TABLE_PLACEHOLDER@", self.app.user_bindings.get_formatted_global_bindings()
        )
        yield MarkdownViewer(new_content, show_table_of_contents=False)

    def action_toggle_table_of_contents(self) -> None:
        self.markdown_viewer.show_table_of_contents = not self.markdown_viewer.show_table_of_contents

    async def action_back(self) -> None:
        await self.markdown_viewer.back()

    async def action_forward(self) -> None:
        await self.markdown_viewer.forward()

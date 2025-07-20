from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.binding import Binding
from textual.widgets import MarkdownViewer

from clive.__private.core.constants.env import ROOT_DIRECTORY
from clive.__private.ui.bindings import CLIVE_PREDEFINED_BINDINGS
from clive.__private.ui.screens.base_screen import BaseScreen

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult


class Help(BaseScreen):
    """
    The help screen for the application.

    Attributes:
        BINDINGS: List of key bindings for the help screen.
        GLOBAL_HELP_FILE_PATH: Path to the global help markdown file.
        SHOW_RAW_HEADER: Whether to show the raw header in this screen.
    """

    BINDINGS = [
        Binding("q,escape", "app.pop_screen", "Back", key_display="esc"),
        CLIVE_PREDEFINED_BINDINGS.help.toggle_help.create(action="app.pop_screen", description="Back", show=False),
        CLIVE_PREDEFINED_BINDINGS.help.toggle_table_of_contents.create(description="Toggle TOC"),
    ]

    GLOBAL_HELP_FILE_PATH: Final[Path] = ROOT_DIRECTORY / "__private/ui/global_help.md"

    SHOW_RAW_HEADER = True

    @property
    def markdown_viewer(self) -> MarkdownViewer:
        """Get the Markdown widget."""
        return self.query_exactly_one(MarkdownViewer)

    def create_main_panel(self) -> ComposeResult:
        content = self.GLOBAL_HELP_FILE_PATH.read_text()
        new_content = self.app.custom_bindings.get_formatted_global_bindings(content)
        yield MarkdownViewer(new_content, show_table_of_contents=False)

    def action_toggle_table_of_contents(self) -> None:
        self.markdown_viewer.show_table_of_contents = not self.markdown_viewer.show_table_of_contents

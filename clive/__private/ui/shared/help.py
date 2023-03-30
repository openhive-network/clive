from __future__ import annotations

import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Final

from textual.binding import Binding
from textual.widgets import MarkdownViewer

from clive.__private.config import ROOT_DIRECTORY
from clive.__private.ui.dashboard.dashboard_base import DashboardBase
from clive.__private.ui.shared.base_screen import BaseScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.screen import Screen


class Help(BaseScreen):
    """The help screen for the application. Created dynamically, based on previously active screen."""

    BINDINGS = [
        Binding("space,q,question_mark,escape", "pop_screen", "Cancel", key_display="ESC"),
    ]

    GLOBAL_HELP_FILE_PATH: Final[Path] = ROOT_DIRECTORY / "ui/global_help.md"

    def __init__(self, screen: Screen) -> None:
        super().__init__()

        self.__screen = screen

        if isinstance(screen, DashboardBase):
            self.__help_file_path = self.GLOBAL_HELP_FILE_PATH
        else:
            class_path = Path(inspect.getfile(screen.__class__))
            self.__help_file_path = class_path.parent / "help.md"

    def create_main_panel(self) -> ComposeResult:
        if self.__help_file_path.exists():
            yield MarkdownViewer(self.__help_file_path.read_text())
        else:
            screen_name = self.__screen.name or self.__screen.__class__.__name__
            context_help_unavailable_text = f"""
**Looks like there is no help available for this screen ({screen_name}). \
Global help is shown below instead.**
"""
            yield MarkdownViewer(context_help_unavailable_text + self.GLOBAL_HELP_FILE_PATH.read_text())

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.terminal.command_line import CommandLine
from clive.__private.ui.terminal.logs import Logs

if TYPE_CHECKING:
    from textual.app import ComposeResult


class TerminalScreen(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__, name="terminal")]

    BINDINGS = [
        Binding("colon", "focus('command-line-input')", "Command line", show=False),
        Binding("ctrl+o", "pop_screen", show=False),
        Binding("escape", "pop_screen", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.__logs = Logs()
        self.__command_line = CommandLine(focus_on_cancel=self.__logs)

    def create_main_panel(self) -> ComposeResult:
        yield self.__logs
        yield self.__command_line

    def on_mount(self) -> None:
        self.__command_line.focus()

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container
from textual.widgets import Input

from clive.ui.terminal.command_line import CommandLine
from clive.ui.terminal.logs import Logs
from clive.ui.widgets.modal import Modal

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Terminal(Modal, Container):
    def __init__(self) -> None:
        super().__init__(classes="-hidden")

    def compose(self) -> ComposeResult:
        yield Logs()
        yield CommandLine()

    def on_mount(self) -> None:
        self.watch(self.app, "terminal_expanded", self.on_terminal_expanded)

    def on_terminal_expanded(self, expanded: bool) -> None:
        if not expanded:
            self.add_class("-hidden")
            self._restore_focus()
        else:
            self.remove_class("-hidden")
            self.query_one(Logs).scroll_end(animate=False)
            self._override_focus()

    def _focus_after_overriding(self) -> None:
        self.query_one(Input).focus()

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container
from textual.widgets import Input, TextLog

from clive.ui.widgets.modal import Modal

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult


class Logs(TextLog):
    def __init__(self) -> None:
        super().__init__(wrap=True, highlight=True, markup=True)

    def on_mount(self) -> None:
        self.watch(self.app, "logs", self.on_logs)  # type: ignore # https://github.com/Textualize/textual/issues/1805

    def on_logs(self, logs: list[RenderableType | object]) -> None:
        last_line_index = len(self.lines)
        for log in logs[last_line_index:]:
            self.write(log)


class Terminal(Modal, Container):
    def __init__(self) -> None:
        super().__init__(classes="-hidden")

    def compose(self) -> ComposeResult:
        yield Logs()
        yield Input()

    def on_mount(self) -> None:
        self.watch(self.app, "terminal_expanded", self.on_terminal_expanded)  # type: ignore # https://github.com/Textualize/textual/issues/1805

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

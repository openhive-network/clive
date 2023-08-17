from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import RichLog

if TYPE_CHECKING:
    from rich.console import RenderableType


class Logs(RichLog):
    def __init__(self) -> None:
        super().__init__(wrap=True, highlight=True, markup=True)

    def on_mount(self) -> None:
        self.watch(self.app, "logs", self.logs_changed)

    def logs_changed(self, logs: list[RenderableType | object]) -> None:
        last_line_index = len(self.lines)
        for log in logs[last_line_index:]:
            self.write(log)

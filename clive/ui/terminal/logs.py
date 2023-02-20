from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import TextLog

if TYPE_CHECKING:
    from rich.console import RenderableType


class Logs(TextLog):
    def __init__(self) -> None:
        super().__init__(wrap=True, highlight=True, markup=True)

    def on_mount(self) -> None:
        self.watch(self.app, "logs", self.on_logs)  # type: ignore # https://github.com/Textualize/textual/issues/1805

    def on_logs(self, logs: list[RenderableType | object]) -> None:
        last_line_index = len(self.lines)
        for log in logs[last_line_index:]:
            self.write(log)

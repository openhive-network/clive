from __future__ import annotations

from textual.widgets import Static


class Notification(Static):
    def on_mount(self) -> None:
        self.set_timer(3, self.remove)

    def on_click(self) -> None:
        self.remove()

    def send(self) -> None:
        self.app.mount(self)

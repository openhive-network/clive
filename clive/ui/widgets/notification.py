from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from textual.widgets import Static

if TYPE_CHECKING:
    from rich.console import RenderableType


class Notification(Static):
    def __init__(
        self, renderable: RenderableType, *, category: Literal["success", "info", "warning", "error"] | None = None
    ) -> None:
        super().__init__(self.__format_renderable(renderable, category))

        if category:
            self.add_class(category)

    def on_mount(self) -> None:
        self.set_timer(3, self.remove)

    def on_click(self) -> None:
        self.remove()

    def send(self) -> None:
        self.app.mount(self)

    @staticmethod
    def __format_renderable(
        renderable: RenderableType, category: Literal["success", "info", "warning", "error"] | None = None
    ) -> RenderableType:
        if category == "success":
            return f"✅ {renderable}"
        elif category == "info":
            return f"ℹ️  {renderable}"  # noqa: RUF001
        elif category == "warning":
            return f"📢 {renderable}"
        elif category == "error":
            return f"⚠️  {renderable}"
        else:
            return renderable

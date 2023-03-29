from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal

from textual.widgets import Static

if TYPE_CHECKING:
    from rich.console import RenderableType


class Notification(Static):
    __EMOJIS: Final[dict[str, str]] = {
        "success": "✅",
        "info": "ℹ️",  # noqa: RUF001
        "warning": "📢",
        "error": "⚠️",
    }

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

    def show(self) -> None:
        self.app.mount(self)

    @classmethod
    def __format_renderable(
        cls, renderable: RenderableType, category: Literal["success", "info", "warning", "error"] | None = None
    ) -> RenderableType:
        return f"{cls.__EMOJIS[category]}  {renderable}" if category in cls.__EMOJIS else renderable

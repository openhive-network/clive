from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from textual.widgets import Static

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual import events


class FocusableLink(Static, can_focus=True):
    def __init__(self, renderable: RenderableType, action: Callable[[], None]) -> None:
        self.__renderable = renderable
        self.__action = action
        super().__init__(self.__create_linked_renderable())

    def action_trigger(self) -> None:
        self.__action()

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.action_trigger()

    def watch_has_focus(self, value: bool) -> None:
        if value:
            self.update(self.__create_linked_renderable(prefix="> "))
        else:
            self.update(self.__create_linked_renderable())

    def __create_linked_renderable(self, prefix: RenderableType = "") -> RenderableType:
        return f"[@click='trigger']{prefix}{self.__renderable}[/]"

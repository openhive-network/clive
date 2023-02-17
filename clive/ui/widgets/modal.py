from __future__ import annotations

from typing import Any

from textual.widget import Widget

from clive.abstract_class import AbstractClassMessagePump


class Modal(Widget, AbstractClassMessagePump):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self.__focus_chain_modified: list[Widget] = []
        self.__previously_focused: Widget | None = None

    def _focus_after_overriding(self) -> None:
        self.focus()

    def _override_focus(self) -> None:
        """Remove focus for everything, force it to the current widget."""
        self.__previously_focused = self.app.focused

        for widget in self.app.screen.focus_chain:
            self.__focus_chain_modified.append(widget)
            widget.can_focus = False
        self._focus_after_overriding()

    def _restore_focus(self) -> None:
        """Restore focus to what it was before."""
        while self.__focus_chain_modified:
            self.__focus_chain_modified.pop().can_focus = True

        if self.__previously_focused is not None and self.__previously_focused in self.app.screen.focus_chain:
            self.app.set_focus(self.__previously_focused)
        else:
            self.app.set_focus(self.app.screen.focus_chain[0])

from __future__ import annotations

from textual.screen import Screen

from clive.ui.widgets.clive_widget import CliveWidget


class CliveScreen(Screen, CliveWidget):
    """
    An ordinary textual screen that also knows what type of application it belongs to.

    Inspired by: https://github.com/Textualize/textual/discussions/1099#discussioncomment-4049612
    """

    def on_mount(self) -> None:
        if self.app.focused is None:
            self.focus_next()

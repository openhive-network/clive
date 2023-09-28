from __future__ import annotations

from clive.__private.ui.widgets.clive_widget import CliveWidget


class CanFocusWithScrollbarsOnly(CliveWidget, can_focus=False):
    """A Widget that can be focused only when scrollbar is active."""

    def on_resize(self) -> None:
        self.__enable_focus_only_when_scrollbar_is_active()

    def __enable_focus_only_when_scrollbar_is_active(self) -> None:
        if any(self.scrollbars_enabled):
            self.can_focus = True
        else:
            self.can_focus = False

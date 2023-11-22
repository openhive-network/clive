from __future__ import annotations

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.widgets.clive_widget import CliveWidget


class CanFocusWithScrollbarsOnly(CliveWidget, AbstractClassMessagePump):
    """
    A Widget that can be focused only when scrollbar is active.

    Inherit from this class to make a widget focusable only when any scrollbar is active.
    """

    def on_mount(self) -> None:
        self.__enable_focus_only_when_scrollbar_is_active()

    def watch_show_vertical_scrollbar(self) -> None:
        self.__enable_focus_only_when_scrollbar_is_active()

    def watch_show_horizontal_scrollbar(self) -> None:
        self.__enable_focus_only_when_scrollbar_is_active()

    def __enable_focus_only_when_scrollbar_is_active(self) -> None:
        self.can_focus = any(self.scrollbars_enabled)

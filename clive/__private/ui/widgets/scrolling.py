from __future__ import annotations

from textual.containers import VerticalScroll

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.clive_widget import CliveWidget


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

        # START WORKAROUND FOR https://github.com/Textualize/textual/issues/5605>>>
        # based on:
        # https://github.com/Textualize/textual/blob/dd36b696ecf2c3f7ae75b1f63671ecab1c8f04cb/src/textual/screen.py#L1324
        auto_focus = self.app.AUTO_FOCUS if self.screen.AUTO_FOCUS is None else self.screen.AUTO_FOCUS
        if auto_focus and self.app.focused is None:
            for widget in self.screen.query(auto_focus):
                if widget.focusable:
                    self.screen.set_focus(widget)
                    break
        # <<<END WORKAROUND


class ScrollablePartFocusable(VerticalScroll, CanFocusWithScrollbarsOnly):
    """Scrollable part of screens that does not contain elements to focus e.g.: Cart."""


class ScrollablePart(VerticalScroll, can_focus=False):
    """Scrollable part of the screens that have elements to focus on, so scroll is going down automatically."""

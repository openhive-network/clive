from __future__ import annotations

from textual.binding import Binding
from textual.containers import VerticalScroll

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.clive_widget import CliveWidget


class CanFocusWithScrollbarsOnly(CliveWidget, AbstractClassMessagePump):
    """
    A Widget that can be focused only when scrollbar is active.

    Inherit from this class to make a widget focusable only when any scrollbar is active.
    """

    def allow_focus(self) -> bool:
        # Known issue: https://github.com/Textualize/textual/issues/5609
        return any(self.scrollbars_enabled)


class ScrollablePartFocusable(VerticalScroll, CanFocusWithScrollbarsOnly):
    """Scrollable part of screens that does not contain elements to focus e.g.: Cart."""


class ScrollablePart(VerticalScroll, can_focus=False):
    """Scrollable part of the screens that have elements to focus on, so scroll is going down automatically."""


class ScrollablePartWithArrowBinding(ScrollablePart):
    """Same as ScrollablePart but additionally supports vertical arrow keys to navigate through elements.

    Attributes:
        BINDINGS: Key bindings for the widget.
    """

    BINDINGS = [
        Binding("up", "app.focus_previous", "Previous", show=False),
        Binding("down", "app.focus_next", "Next", show=False),
    ]

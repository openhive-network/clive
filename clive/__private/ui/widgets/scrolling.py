from __future__ import annotations

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

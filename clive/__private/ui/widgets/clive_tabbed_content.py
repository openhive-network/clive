from __future__ import annotations

from itertools import zip_longest
from typing import TYPE_CHECKING, ClassVar

from textual.binding import Binding, BindingType
from textual.widgets import ContentSwitcher, TabbedContent, TabPane
from textual.widgets._tabbed_content import ContentTab, ContentTabs

if TYPE_CHECKING:
    from textual.app import ComposeResult


class CliveTabs(ContentTabs):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("left", "previous_tab", "Previous tab", show=True),
        Binding("right", "next_tab", "Next tab", show=True),
    ]


class CliveTabbedContent(TabbedContent):
    """A tabbed content that shows "left" and "right" bindings in the footer when header (Tabs) is focused."""

    def compose(self) -> ComposeResult:
        pane_content = [
            self._set_id(
                content if isinstance(content, TabPane) else TabPane(title or self.render_str(f"Tab {index}"), content),
                index,
            )
            for index, (title, content) in enumerate(zip_longest(self.titles, self._tab_content), 1)
        ]
        # Get a tab for each pane
        tabs = [ContentTab(content._title, content.id or "") for content in pane_content]
        # Yield the tabs
        yield CliveTabs(*tabs, active=self._initial or None, tabbed_content=self)
        # Yield the content switcher and panes
        with ContentSwitcher(initial=self._initial or None):
            yield from pane_content

    def get_child_by_type(self, expect_type: type[TabbedContent.ExpectType]) -> TabbedContent.ExpectType:
        """Returns CliveTabs instead of Tabs because get_child_by_type checks for the exact type (not subclasses)."""
        if expect_type is ContentTabs:
            for child in self._nodes:
                if isinstance(child, CliveTabs):
                    return child  # type: ignore[return-value]

        return super().get_child_by_type(expect_type)

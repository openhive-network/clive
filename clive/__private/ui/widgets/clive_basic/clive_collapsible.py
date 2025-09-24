from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import HorizontalGroup, Right
from textual.widget import Widget
from textual.widgets import Collapsible, Label

from clive.__private.ui.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult


class CliveCollapsible(Collapsible, CliveWidget):
    DEFAULT_CSS = """
    CliveCollapsible {
        border-top: none;
        padding-bottom: 0;

        CollapsibleTitle {
            background: $primary;

            &:focus {
                background: white;
            }

            &:hover {
                background: $primary-darken-1;
            }
        }

        #right-hand-side-text {
            margin-right: 1;
        }
    }
    """

    def __init__(
        self,
        *children: Widget,
        title: str = "Toggle",
        collapsed: bool = True,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        right_hand_side_content: str | Widget | None = None,
    ) -> None:
        super().__init__(*children, title=title, collapsed=collapsed, id=id_, classes=classes, disabled=disabled)
        self._right_hand_side_content = right_hand_side_content

    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            yield self._title
            yield from self._create_right_hand_side_content()
        yield self.Contents(*self._contents_list)

    def _create_right_hand_side_content(self) -> ComposeResult:
        content = self._right_hand_side_content

        if content is None:
            return

        with Right():
            if isinstance(content, Widget):
                yield content
            elif isinstance(content, str):
                yield Label(content, id="right-hand-side-text")

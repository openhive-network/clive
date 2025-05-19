from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import HorizontalGroup, Right
from textual.widgets import Collapsible, Static

from clive.__private.ui.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget


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
            width: auto;
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
        right_hand_side_text: str | None = None,
    ) -> None:
        super().__init__(*children, title=title, collapsed=collapsed, id=id_, classes=classes, disabled=disabled)
        self._right_hand_side_text = right_hand_side_text

    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            yield self._title
            if self._right_hand_side_text:
                with Right():
                    yield Static(self._right_hand_side_text, id="right-hand-side-text")
        yield self.Contents(*self._contents_list)

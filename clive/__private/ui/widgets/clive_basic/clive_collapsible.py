from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal
from textual.widgets import Collapsible, Static

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget


class CliveCollapsible(Collapsible):
    DEFAULT_CSS = """
    CliveCollapsible {
        margin-bottom: 1;
        border-top: none;

        CollapsibleTitle {
            background: $primary;

            &:focus {
                background: white;
            }

            &:hover {
                background: $primary-darken-1;
            }
        }

        CliveCollapsible.-collapsed {
            padding-bottom: 0;
        }

        #title-container {
            width: 1fr;
            height: auto;

            #right-hand-side-text-container {
                align-horizontal: right;
                height: auto;

                #right-hand-side-text {
                    align: right middle;
                    margin-right: 1;
                    width: auto;
                }
            }
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
        yield Horizontal(
            self._title,
            Container(
                Static(self._right_hand_side_text if self._right_hand_side_text else "", id="right-hand-side-text"),
                id="right-hand-side-text-container",
            ),
            id="title-container",
        )
        yield self.Contents(*self._contents_list)

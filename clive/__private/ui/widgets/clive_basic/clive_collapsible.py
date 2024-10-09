from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Collapsible

if TYPE_CHECKING:
    from textual.widget import Widget


class CliveCollapsible(Collapsible):
    DEFAULT_CSS = """
    CliveCollapsible {
        CollapsibleTitle {
            background: $primary;

            &:focus {
                background: white;
            }

            &:hover {
                background: $primary-darken-1;
            }
        }
    }
    """

    def __init__(
        self,
        *children: Widget,
        title: str = "Toggle",
        collapsed: bool = True,
        collapsed_symbol: str = "▲",
        expanded_symbol: str = "▼",
        name: str | None = None,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            *children,
            title=title,
            collapsed=collapsed,
            collapsed_symbol=collapsed_symbol,
            expanded_symbol=expanded_symbol,
            name=name,
            id=id_,
            classes=classes,
            disabled=disabled,
        )

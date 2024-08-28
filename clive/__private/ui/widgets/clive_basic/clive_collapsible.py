from __future__ import annotations

from textual.widgets import Collapsible


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

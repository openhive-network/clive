from __future__ import annotations

from typing import TYPE_CHECKING, cast

from textual.widgets import Footer
from textual.widgets._footer import FooterKey

if TYPE_CHECKING:
    from textual.app import ComposeResult


class CliveFooter(Footer):
    def compose(self) -> ComposeResult:
        widgets = list(super().compose())
        for widget in widgets:
            assert isinstance(widget, FooterKey), f"{widget} is not a FooterKey"
        return self._order_keys(cast("list[FooterKey]", widgets))

    def _order_keys(self, footer_keys: list[FooterKey]) -> list[FooterKey]:
        """
        Order footer keys.

        The order is:
            1. Prioritized keys
            2. Rest of the keys defined by Textual order

        Args:
            footer_keys: The footer keys to order.

        Returns:
            Ordered footer keys.
        """
        prioritized = {"escape", "question_mark"}
        prioritized_matches = [fk for fk in footer_keys if fk.key in prioritized]
        remaining = [fk for fk in footer_keys if fk.key not in prioritized]
        return prioritized_matches + remaining

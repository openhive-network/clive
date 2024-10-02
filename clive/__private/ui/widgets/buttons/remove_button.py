from __future__ import annotations

from clive.__private.ui.widgets.buttons import CliveButton


class ButtonRemove(CliveButton):
    """Button used for removing the operation from cart."""

    def __init__(self) -> None:
        super().__init__("X", id_="delete-button", variant="error")

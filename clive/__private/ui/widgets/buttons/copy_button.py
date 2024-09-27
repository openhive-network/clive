from __future__ import annotations

from clive.__private.ui.widgets.buttons import OneLineButton


class CopyButton(OneLineButton):
    class Pressed(OneLineButton.Pressed):
        """Used to identify exactly that copy button was pressed."""

    def __init__(self, label: str = "Copy") -> None:
        super().__init__(label=label, variant="success")

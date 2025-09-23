from __future__ import annotations

from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class RestoreButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that RestoreButton button was pressed."""

    def __init__(self, label: str = "Restore", id_: str = "restore-button") -> None:
        super().__init__(label, variant="error", id_=id_)


class RestoreOneLineButton(OneLineButton, RestoreButton):
    class Pressed(RestoreButton.Pressed):
        """Used to identify exactly that RestoreOneLineButton was pressed."""

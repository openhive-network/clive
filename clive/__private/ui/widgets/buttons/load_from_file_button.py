from __future__ import annotations

from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class LoadFromFileButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that LoadFromFileButton was pressed."""

    def __init__(self, label: str = "Load from file", id_: str = "load-from-file-button") -> None:
        super().__init__(label=label, variant="success", id_=id_)


class LoadFromFileOneLineButton(OneLineButton, LoadFromFileButton):
    class Pressed(LoadFromFileButton.Pressed):
        """Used to identify exactly that LoadFromFileOneLineButton was pressed."""

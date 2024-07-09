from __future__ import annotations

from textual import on

from clive.__private.ui.widgets.one_line_button import OneLineButton


class CancelButton(OneLineButton):
    def __init__(self, label: str = "Cancel", *, pop_screen_on_click: bool = True) -> None:
        super().__init__(label, variant="error", id_="cancel-button")
        self._pop_screen_on_click = pop_screen_on_click

    @on(OneLineButton.Pressed, "#cancel-button")
    def close_screen(self) -> None:
        if self._pop_screen_on_click:
            self.app.pop_screen()

from __future__ import annotations

from clive.__private.ui.widgets.buttons.clive_button import CliveButton


class SearchButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Message send when SearchButton is pressed."""

    def __init__(self, label: str = "Search", id_: str = "search-button") -> None:
        super().__init__(label=label, id_=id_, variant="success")


class ClearButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Message send when ClearButton is pressed."""

    def __init__(self, label: str = "Clear", id_: str = "clear-button") -> None:
        super().__init__(label=label, id_=id_, variant="error")

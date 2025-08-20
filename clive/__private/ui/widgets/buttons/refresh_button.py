from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton

if TYPE_CHECKING:
    from clive.__private.ui.bindings.clive_binding import CliveBinding


class RefreshButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Message sent when RefreshButton is pressed."""

    def __init__(
        self, label: str = "Refresh", *, binding: CliveBinding | None = None, id_: str = "button-refresh"
    ) -> None:
        super().__init__(label, binding=binding, id_=id_)


class RefreshOneLineButton(OneLineButton, RefreshButton):
    class Pressed(RefreshButton.Pressed):
        """Message sent when RefreshOneLineButton is pressed."""

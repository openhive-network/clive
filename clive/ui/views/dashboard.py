from __future__ import annotations

from typing import TYPE_CHECKING, Union

from prompt_toolkit.key_binding import KeyBindings

from clive.ui.components.buttons_menu_first import ButtonsMenuFirst
from clive.ui.components.left_component import LeftComponentFirst
from clive.ui.components.side_panel import SidePanel
from clive.ui.views.side_pane_based import SidePanelBased

if TYPE_CHECKING:
    from clive.ui.components.buttons_menu_second import ButtonsMenuSecond  # noqa: F401
    from clive.ui.components.left_component import LeftComponentSecond  # noqa: F401


Main = Union[LeftComponentFirst, "LeftComponentSecond"]
Side = SidePanel
Buttons = Union[ButtonsMenuFirst, "ButtonsMenuSecond"]


class Dashboard(SidePanelBased[Main, Side, Buttons]):
    def __init__(self) -> None:
        self.__key_bindings: list[KeyBindings] = []

        super().__init__(LeftComponentFirst(self), SidePanel(self), ButtonsMenuFirst(self))

    @property
    def key_bindings(self) -> list[KeyBindings]:
        return self.__key_bindings

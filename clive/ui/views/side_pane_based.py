from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Generic, TypeVar

from clive.ui.views.button_based import ButtonsBased

if TYPE_CHECKING:
    from typing import Any  # noqa: F401

    from clive.ui.component import Component  # noqa: F401
    from clive.ui.components.buttons_menu import ButtonsMenu  # noqa: F401
    from clive.ui.components.side_panel import SidePanel  # noqa: F401


M = TypeVar("M", bound="Component[SidePanel[Any, Any]]")
S = TypeVar("S", bound="Component[SidePanel[Any, Any]]")
B = TypeVar("B", bound="ButtonsMenu[Any]")


class SidePanelBased(ButtonsBased["SidePanel[M,S]", "ButtonsMenu[SidePanelBased[M, S, B]]"], Generic[M, S, B], ABC):
    def __init__(self, side_panel: SidePanel[M, S], buttons: B) -> None:
        self._side_panel = side_panel
        super().__init__(self._side_panel, buttons)

    @property  # type: ignore
    def main_panel(self) -> M:
        return self._side_panel.main_panel

    @main_panel.setter
    def main_panel(self, value: M) -> None:
        self._side_panel.main_panel = value

    @property
    def side_panel(self) -> S:
        return self._side_panel.side_panel

    @property
    def buttons(self) -> B:
        return self._buttons  # type: ignore

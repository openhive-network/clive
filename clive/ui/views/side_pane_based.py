from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from clive.abstract_class import AbstractClass
from clive.ui.components.side_panel_splitter import SidePanelSplitter
from clive.ui.views.button_based import ButtonsBased

if TYPE_CHECKING:
    from typing import Any  # noqa: F401

    from clive.ui.component import Component  # noqa: F401
    from clive.ui.components.buttons_menu import ButtonsMenu  # noqa: F401


M = TypeVar("M", bound="Component[Any]")
S = TypeVar("S", bound="Component[Any]")
B = TypeVar("B", bound="ButtonsMenu[Any]")


class SidePanelBased(
    ButtonsBased["SidePanelSplitter[M,S]", "ButtonsMenu[SidePanelBased[M, S, B]]"], Generic[M, S, B], AbstractClass
):
    def __init__(self, main_panel: M, side_panel: S, buttons: B) -> None:
        self.__splitter = SidePanelSplitter(self, main_panel, side_panel)
        super().__init__(self.__splitter, buttons)

    @property  # type: ignore
    def main_panel(self) -> M:
        return self.__splitter.main_panel

    @main_panel.setter
    def main_panel(self, value: M) -> None:
        self.__splitter.main_panel = value

    @property
    def side_panel(self) -> S:
        return self.__splitter.side_panel

    @property
    def buttons(self) -> B:
        return self._buttons  # type: ignore

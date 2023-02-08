from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Sequence, TypeVar

from clive.abstract_class import AbstractClass
from clive.enums import AppMode
from clive.ui.components.side_panel_splitter import SidePanelSplitter
from clive.ui.views.button_based import ButtonsBased

if TYPE_CHECKING:
    from typing import Any

    from clive.ui.component import Component
    from clive.ui.components.buttons_menu import ButtonsMenu


M = TypeVar("M", bound="Component[Any]")
S = TypeVar("S", bound="Component[Any]")
B = TypeVar("B", bound="ButtonsMenu[Any]")


class SidePanelBased(
    ButtonsBased["SidePanelSplitter[M,S]", "ButtonsMenu[SidePanelBased[M, S, B]]"], Generic[M, S, B], AbstractClass
):
    def __init__(
        self, main_panel: M, side_panel: S, buttons: B, *, available_in_modes: Sequence[AppMode] = (AppMode.ANY,)
    ) -> None:
        self.__splitter = SidePanelSplitter(self, main_panel, side_panel)
        super().__init__(self.__splitter, buttons, available_in_modes=available_in_modes)

    @property  # type: ignore
    def main_panel(self) -> M:
        return self.__splitter.main_panel

    @main_panel.setter
    def main_panel(self, value: M) -> None:
        self.__splitter.main_panel = value
        self._rebuild()

    @property
    def side_panel(self) -> S:
        return self.__splitter.side_panel

    @side_panel.setter
    def side_panel(self, value: S) -> None:
        self.__splitter.side_panel = value
        self._rebuild()

    @property  # type: ignore
    def buttons(self) -> B:
        return super().buttons  # type: ignore

    @buttons.setter
    def buttons(self, value: B) -> None:
        super()._set_buttons(value)
        self._rebuild()

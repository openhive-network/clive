from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from prompt_toolkit.layout import Dimension, VSplit
from prompt_toolkit.widgets import Frame, Label

from clive.ui.component import Component

if TYPE_CHECKING:
    from typing import Any  # noqa: F401

    from prompt_toolkit.layout.containers import AnyContainer

    from clive.ui.views.side_pane_based import SidePanelBased


M = TypeVar("M", bound="Component[SidePanel[Any, Any]]")
S = TypeVar("S", bound="Component[SidePanel[Any, Any]]")


class SidePanel(Component["SidePanelBased[M, S, Any]"], Generic[M, S]):
    def __init__(
        self, parent: SidePanelBased[M, S, Any], main_panel: M | None = None, side_panel: S | None = None
    ) -> None:
        self.__main_panel = main_panel
        self.__side_panel = side_panel
        super().__init__(parent)

    def _create_container(self) -> VSplit:
        return VSplit(
            [
                Frame(self.__get_main_panel_container(), width=Dimension(weight=3)),
                Frame(self.__get_side_panel_container()),
            ],
            style="class:primary",
        )

    def __get_main_panel_container(self) -> AnyContainer:
        return self.__main_panel.container if self.__main_panel else Label(text="Main panel not set")

    def __get_side_panel_container(self) -> AnyContainer:
        return self.__side_panel.container if self.__side_panel else Label(text="Side panel not set")

    def set_main_panel_first_time(self, main_panel: M) -> None:
        self.__main_panel = main_panel
        self._rebuild(self_only=True)

    def set_side_panel_first_time(self, side_panel: S) -> None:
        self.__side_panel = side_panel
        self._rebuild(self_only=True)

    @property
    def main_panel(self) -> M:
        assert self.__main_panel is not None, "Main pane was not set."
        return self.__main_panel

    @main_panel.setter
    def main_panel(self, value: M) -> None:
        self.__main_panel = value
        self._rebuild()

    @property
    def side_panel(self) -> S:
        assert self.__side_panel is not None, "Side pane was not set."
        return self.__side_panel

    @side_panel.setter
    def side_panel(self, value: S) -> None:
        self.__side_panel = value
        self._rebuild()

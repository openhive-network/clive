from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from prompt_toolkit.layout import Dimension, VSplit
from prompt_toolkit.widgets import Frame

from clive.ui.component import Component

if TYPE_CHECKING:
    from typing import Any  # noqa: F401

    from clive.ui.views.side_pane_based import SidePanelBased

M = TypeVar("M", bound="Component[SidePanelSplitter[Any, Any]]")
S = TypeVar("S", bound="Component[SidePanelSplitter[Any, Any]]")


class SidePanelSplitter(Component["SidePanelBased[M, S, Any]"], Generic[M, S]):
    def __init__(self, parent: SidePanelBased[M, S, Any], main_panel: M, side_panel: S) -> None:
        self.__main_panel = main_panel
        self.__side_panel = side_panel
        super().__init__(parent)

    def _create_container(self) -> VSplit:
        return VSplit(
            [
                Frame(self.__main_panel.container, width=Dimension(weight=3)),
                Frame(self.__side_panel.container),
            ],
            style="class:primary",
        )

    @property
    def main_panel(self) -> M:
        assert self.__main_panel is not None, "Main panel was not set."
        return self.__main_panel

    @main_panel.setter
    def main_panel(self, value: M) -> None:
        self.__main_panel = value
        self._rebuild()

    @property
    def side_panel(self) -> S:
        assert self.__side_panel is not None, "Side panel was not set."
        return self.__side_panel

    @side_panel.setter
    def side_panel(self, value: S) -> None:
        self.__side_panel = value
        self._rebuild()

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Generic, TypeVar

from prompt_toolkit.layout import HSplit
from prompt_toolkit.widgets import Frame

from clive.ui.view import View
from clive.ui.view_manager import view_manager

if TYPE_CHECKING:
    from typing import Any  # noqa: F401

    from clive.ui.component import Component  # noqa: F401
    from clive.ui.components.buttons_menu import ButtonsMenu  # noqa: F401


M = TypeVar("M", bound="Component[Any]")
B = TypeVar("B", bound="ButtonsMenu[Any]")


class ButtonsBased(View, Generic[M, B], ABC):
    def __init__(self, main_pane: M, buttons: B) -> None:
        self._main_panel = main_pane
        self._buttons = buttons
        super().__init__(view_manager)

    def _create_container(self) -> HSplit:
        return HSplit(
            [
                self._main_panel.container,
                Frame(self._buttons.container, style="class:primary"),
            ],
            style="class:primary",
            key_bindings=self._buttons.key_bindings,
        )

    @property
    def main_panel(self) -> M:
        return self._main_panel

    @main_panel.setter
    def main_panel(self, value: M) -> None:
        self._main_panel = value
        self._rebuild()

    @property
    def buttons(self) -> B:
        return self._buttons

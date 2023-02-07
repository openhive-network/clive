from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List, TypeVar

from prompt_toolkit.layout import HorizontalAlign, VSplit

from clive.ui.component import Component

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.widgets import Button

T = TypeVar("T", bound=Component[Any])


class ButtonsMenu(Component[T], ABC):
    def __init__(self, parent: T) -> None:
        self._buttons: List[Button] = self._create_buttons()
        self._key_bindings = self._get_key_bindings()
        super().__init__(parent)

    def _create_container(self) -> VSplit:
        return VSplit(
            self._buttons,
            align=HorizontalAlign.LEFT,
            padding=1,
        )

    @property
    def key_bindings(self) -> KeyBindings:
        return self._key_bindings

    @abstractmethod
    def _create_buttons(self) -> List[Button]:
        """Creates buttons for the component."""

    @abstractmethod
    def _get_key_bindings(self) -> KeyBindings:
        """Creates key bindings for the component."""

    def _rebuild(self) -> None:
        self._buttons = self._create_buttons()
        super()._rebuild()

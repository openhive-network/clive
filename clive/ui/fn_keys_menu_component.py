from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Sequence

from prompt_toolkit.layout import HorizontalAlign, VSplit
from prompt_toolkit.widgets import Button

from clive.ui.component import Component

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyBindings


class FnKeysMenuComponent(Component, ABC):
    def __init__(self) -> None:
        self._buttons = self._create_buttons()
        self._key_bindings = self._get_key_bindings()
        super().__init__()

    def _create_container(self) -> VSplit:
        return VSplit(
            self._buttons,
            align=HorizontalAlign.LEFT,
            padding=1,
        )

    @abstractmethod
    def _create_buttons(self) -> Sequence[Button]:
        """Creates buttons for the component."""

    @abstractmethod
    def _get_key_bindings(self) -> KeyBindings:
        """Creates key bindings for the component."""

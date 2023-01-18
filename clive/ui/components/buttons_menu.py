from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TYPE_CHECKING, Sequence, TypeVar

from prompt_toolkit.layout import HorizontalAlign, VSplit
from prompt_toolkit.widgets import Button

from clive.ui.component import Component, DynamicComponent

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyBindings

T = TypeVar("T")


class ButtonsMenu(DynamicComponent, ABC):
    def __init__(self) -> None:
        self._buttons = self._create_buttons()
        super().__init__()
        self._context = None
        self._key_bindings = self._get_key_bindings()

    @property
    def context(self) -> T:
        assert self._context is not None, f"{self} context is not set yet."
        return self._context

    @context.setter
    def context(self, value: T) -> None:
        self._context = value
        value.key_bindings.append(self._key_bindings)

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

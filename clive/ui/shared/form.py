from __future__ import annotations

from abc import abstractmethod
from typing import Callable, Iterator, List

from clive.ui.shared.form_screen import FormScreen  # noqa: TCH001
from clive.ui.widgets.clive_screen import CliveScreen

ScreenBuilder = Callable[[], FormScreen]


class Form(CliveScreen):
    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        self.__current_screen_index = 0
        self.__screens: List[ScreenBuilder] = list(self.register_screen_builders())
        assert len(self.__screens) > 0, "no screen given to display"

        super().__init__(name, id, classes)

    def on_mount(self) -> None:
        assert self.__current_screen_index == 0
        self.__push_current_screen()

    def action_next_screen(self) -> None:
        if not self.__check_valid_range(self.__current_screen_index + 1):
            return

        self.__current_screen_index += 1
        self.__push_current_screen()

    def action_previous_screen(self) -> None:
        if not self.__check_valid_range(self.__current_screen_index - 1):
            return

        self.__current_screen_index -= 1
        self.__pop_current_screen()

    def __push_current_screen(self) -> None:
        self.app.push_screen(self.__screens[self.__current_screen_index]().set_form_owner(owner=self))

    def __pop_current_screen(self) -> None:
        self.app.pop_screen().remove()

    def __check_valid_range(self, proposed_idx: int) -> bool:
        return (proposed_idx >= 0) and (proposed_idx < len(self.__screens))

    @abstractmethod
    def register_screen_builders(self) -> Iterator[ScreenBuilder]:
        """Returns screens to display"""

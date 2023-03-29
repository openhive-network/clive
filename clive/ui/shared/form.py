from __future__ import annotations

from abc import abstractmethod
from typing import Callable, Iterator, List

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.shared.dedicated_form_screens.finish_form_screen import FinishFormScreen
from clive.ui.shared.dedicated_form_screens.welcome_form_screen import WelcomeFormScreen
from clive.ui.shared.form_screen import FormScreen
from clive.ui.widgets.clive_screen import CliveScreen

ScreenBuilder = Callable[[], FormScreen | BaseScreen]


class Form(CliveScreen):
    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        self.__current_screen_index = 0
        self.__screens: List[ScreenBuilder] = [self.create_welcome_screen, *list(self.register_screen_builders())]
        assert len(self.__screens) > 1, "no screen given to display"
        self.__screens.append(self.create_finish_screen)

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
        self.app.push_screen(self.__screens[self.__current_screen_index]().set_form_owner(owner=self))  # type: ignore

    def __pop_current_screen(self) -> None:
        self.app.pop_screen().remove()

    def __check_valid_range(self, proposed_idx: int) -> bool:
        return (proposed_idx >= 0) and (proposed_idx < len(self.__screens))

    @abstractmethod
    def register_screen_builders(self) -> Iterator[ScreenBuilder]:
        """Returns screens to display"""

    def create_welcome_screen(self) -> WelcomeFormScreen:
        return WelcomeFormScreen("Let's fill some fields")

    def create_finish_screen(self) -> FinishFormScreen:
        return FinishFormScreen("Hope it didn't take too long")

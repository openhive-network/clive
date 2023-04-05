from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Iterator
from typing import Final

from clive.__private.storage.contextual import ContextT, Contextual
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.dedicated_form_screens.finish_form_screen import FinishFormScreen
from clive.__private.ui.shared.dedicated_form_screens.welcome_form_screen import WelcomeFormScreen
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.clive_screen import CliveScreen

ScreenBuilder = type | Callable[["Form[ContextT]"], FormScreen[ContextT] | BaseScreen]


class Form(Contextual[ContextT], CliveScreen):
    AMOUNT_OF_DEFAULT_SCREENS: Final[int] = 2

    def __init__(self) -> None:
        self.__current_screen_index = 0
        self.__screens: list[ScreenBuilder[ContextT]] = [
            self.create_welcome_screen(),
            *list(self.register_screen_builders()),
            self.create_finish_screen(),
        ]
        assert len(self.__screens) > self.AMOUNT_OF_DEFAULT_SCREENS, "no screen given to display"

        super().__init__()

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
        self.app.push_screen(self.__screens[self.__current_screen_index](self))  # type: ignore

    def __pop_current_screen(self) -> None:
        self.app.pop_screen().remove()

    def __check_valid_range(self, proposed_idx: int) -> bool:
        return (proposed_idx >= 0) and (proposed_idx < len(self.__screens))

    @abstractmethod
    def register_screen_builders(self) -> Iterator[ScreenBuilder[ContextT]]:
        """Returns screens to display"""

    def create_welcome_screen(self) -> ScreenBuilder[ContextT]:
        return lambda owner: WelcomeFormScreen(owner, "Let's fill some fields")

    def create_finish_screen(self) -> ScreenBuilder[ContextT]:
        return lambda owner: FinishFormScreen(owner, "Hope it didn't take too long")

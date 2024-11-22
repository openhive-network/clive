from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Iterator
from queue import Queue
from typing import Any

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.contextual import ContextT, Contextual
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.create_profile.form_screen import FormScreenBase

ScreenBuilder = Callable[["Form[ContextT]"], FormScreenBase[ContextT] | FormScreenBase[None]]
PostAction = Command | Callable[[], Any]


class Form(Contextual[ContextT], CliveScreen[None]):
    MINIMUM_SCREEN_COUNT = 2  # Rationale: it makes no sense to have only one screen in the form

    def __init__(self) -> None:
        self.__current_screen_index = 0
        self.__screens: list[ScreenBuilder[ContextT]] = [*list(self.register_screen_builders())]
        self.__skipped_screens: set[ScreenBuilder[ContextT]] = set()
        assert len(self.__screens) >= self.MINIMUM_SCREEN_COUNT, "Form must have at least 2 screens"
        self._rebuild_context()
        self._post_actions = Queue[PostAction]()

        super().__init__()

    @property
    def screens(self) -> list[ScreenBuilder[ContextT]]:
        return self.__screens

    @property
    def current_screen(self) -> ScreenBuilder[ContextT]:
        return self.__screens[self.__current_screen_index]

    def on_mount(self) -> None:
        assert self.__current_screen_index == 0
        self.__push_current_screen()

    def _skip_during_push_screen(self) -> list[ScreenBuilder[ContextT]]:
        return []

    def action_next_screen(self) -> None:
        if not self.__check_valid_range(self.__current_screen_index + 1):
            return

        self.__current_screen_index += 1

        if self.__is_current_screen_to_skip():
            self.__skipped_screens.add(self.current_screen)
            self.action_next_screen()
            return

        self.__push_current_screen()

    def action_previous_screen(self) -> None:
        if not self.__check_valid_range(self.__current_screen_index - 1):
            return

        self.__current_screen_index -= 1

        if self.__is_current_screen_skipped():
            self.__skipped_screens.discard(self.current_screen)
            self.action_previous_screen()
            return

        # self.dismiss() won't work here because self is Form and not FormScreen
        self.app.pop_screen()

    def __is_current_screen_to_skip(self) -> bool:
        return self.current_screen in self._skip_during_push_screen()

    def __is_current_screen_skipped(self) -> bool:
        return self.current_screen in self.__skipped_screens

    def __push_current_screen(self) -> None:
        self.app.push_screen(self.current_screen(self))

    def __check_valid_range(self, proposed_idx: int) -> bool:
        return (proposed_idx >= 0) and (proposed_idx < len(self.__screens))

    @abstractmethod
    def _rebuild_context(self) -> None:
        """Create brand new fresh context."""

    @abstractmethod
    def register_screen_builders(self) -> Iterator[ScreenBuilder[ContextT]]:
        """Return screens to display."""

    def add_post_action(self, *actions: PostAction) -> None:
        for action in actions:
            self._post_actions.put_nowait(action)

    def clear_post_actions(self) -> None:
        self._post_actions = Queue[PostAction]()

    async def execute_post_actions(self) -> None:
        while not self._post_actions.empty():
            action = self._post_actions.get_nowait()

            if isinstance(action, Command):
                await action.execute()
            else:
                action()

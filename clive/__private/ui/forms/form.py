from __future__ import annotations

import inspect
from abc import abstractmethod
from collections.abc import Callable, Iterator
from queue import Queue
from typing import TYPE_CHECKING, Any

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.contextual import ContextT, Contextual
from clive.__private.ui.clive_screen import CliveScreen

if TYPE_CHECKING:
    from clive.__private.ui.forms.form_screen import FormScreenBase

PostAction = Command | Callable[[], Any]


class Form(Contextual[ContextT], CliveScreen[None]):
    MINIMUM_SCREEN_COUNT = 2  # Rationale: it makes no sense to have only one screen in the form

    def __init__(self) -> None:
        self._current_screen_index = 0
        self._screens: list[type[FormScreenBase[ContextT]]] = [*list(self.register_screen_builders())]
        assert len(self._screens) >= self.MINIMUM_SCREEN_COUNT, "Form must have at least 2 screens"
        self._rebuild_context()
        self._post_actions = Queue[PostAction]()

        super().__init__()

    @property
    def screens(self) -> list[type[FormScreenBase[ContextT]]]:
        return self._screens

    @property
    def current_screen(self) -> type[FormScreenBase[ContextT]]:
        return self._screens[self._current_screen_index]

    def on_mount(self) -> None:
        assert self._current_screen_index == 0
        self._push_current_screen()

    def next_screen(self) -> None:
        if not self._check_valid_range(self._current_screen_index + 1):
            return

        self._current_screen_index += 1

        self._push_current_screen()

    def previous_screen(self) -> None:
        if not self._check_valid_range(self._current_screen_index - 1):
            return

        self._current_screen_index -= 1

        # self.dismiss() won't work here because self is Form and not FormScreen
        self.app.pop_screen()

    def _push_current_screen(self) -> None:
        self.app.push_screen(self.current_screen(self))

    def _check_valid_range(self, proposed_idx: int) -> bool:
        return (proposed_idx >= 0) and (proposed_idx < len(self._screens))

    @abstractmethod
    def _rebuild_context(self) -> None:
        """Create brand new fresh context."""

    @abstractmethod
    def register_screen_builders(self) -> Iterator[type[FormScreenBase[ContextT]]]:
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
            elif inspect.iscoroutinefunction(action):
                await action()
            else:
                action()

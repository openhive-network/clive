from __future__ import annotations

import inspect
from abc import abstractmethod
from collections.abc import Callable, Iterator
from queue import Queue
from typing import TYPE_CHECKING, Any

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.contextual import ContextualHolder
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.forms.form_context import FormContextT, NoContext

if TYPE_CHECKING:
    from clive.__private.ui.forms.form_screen import FormScreenBase

PostAction = Command | Callable[[], Any]


class Form(ContextualHolder[FormContextT], CliveScreen[None]):
    MINIMUM_SCREEN_COUNT = 2  # Rationale: it makes no sense to have only one screen in the form

    def __init__(self) -> None:
        self._current_screen_index = 0
        self._screen_types: list[type[FormScreenBase[FormContextT]]] = [*list(self.compose_form())]
        assert len(self._screen_types) >= self.MINIMUM_SCREEN_COUNT, "Form must have at least 2 screens"
        self._post_actions = Queue[PostAction]()

        super().__init__(self._build_context())

    @abstractmethod
    def compose_form(self) -> Iterator[type[FormScreenBase[FormContextT]]]:
        """Yield screens types in the order they should be displayed."""

    @property
    def screens_types(self) -> list[type[FormScreenBase[FormContextT]]]:
        return self._screen_types

    @property
    def current_screen_type(self) -> type[FormScreenBase[FormContextT]]:
        return self._screen_types[self._current_screen_index]

    async def on_mount(self) -> None:
        assert self._current_screen_index == 0
        await self.initialize()
        self._push_current_screen()

    async def initialize(self) -> None:
        """Do actions that should be executed before the first form is displayed."""

    async def cleanup(self) -> None:
        """Do actions that should be executed when exiting the form."""

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

    def _build_context(self) -> FormContextT:
        return NoContext()  # type: ignore[return-value]

    def _push_current_screen(self) -> None:
        self.app.push_screen(self.current_screen_type(self))

    def _check_valid_range(self, proposed_idx: int) -> bool:
        return (proposed_idx >= 0) and (proposed_idx < len(self._screen_types))

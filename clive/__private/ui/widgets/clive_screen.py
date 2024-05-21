from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, ParamSpec

from textual import on
from textual.events import ScreenResume, ScreenSuspend
from textual.message import Message
from textual.screen import Screen, ScreenResultType

from clive.__private.core.commands.abc.command_in_active import CommandRequiresActiveModeError
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from textual.widget import Widget

    from clive.__private.ui.app import Clive
    from clive.__private.ui.types import ActiveBindingsMap


P = ParamSpec("P")


class OnlyInActiveModeError(CliveError):
    """Should be raised when some action is only available in active mode."""


class CliveScreen(Screen[ScreenResultType], CliveWidget):
    """
    An ordinary textual screen that also knows what type of application it belongs to.

    Inspired by: https://github.com/Textualize/textual/discussions/1099#discussioncomment-4049612
    """

    class Suspended(Message):
        """Message to notify children widgets that the screen they were mounted on, was suspended."""

    class Resumed(Message):
        """Message to notify children widgets that the screen they were mounted on, was resumed."""

    @property
    def active_bindings(self) -> ActiveBindingsMap:
        """Provides the ability to control the binding order in the footer."""
        return self._sort_bindings(super().active_bindings)

    @staticmethod
    def try_again_after_activation(
        *, app: Clive | None = None
    ) -> Callable[[Callable[P, Awaitable[None]]], Callable[P, Awaitable[None]]]:
        def decorator(func: Callable[P, Awaitable[None]]) -> Callable[P, Awaitable[None]]:
            @wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
                if not app:
                    self = args[0]
                    assert isinstance(self, CliveWidget), f"{type(self)} is not a CliveWidget"
                    app_ = self.app
                else:
                    app_ = app

                try:
                    await func(*args, **kwargs)
                except (CommandRequiresActiveModeError, OnlyInActiveModeError):
                    from clive.__private.ui.activate.activate import Activate

                    async def _on_activation_result(value: bool) -> None:
                        if not value:
                            app_.notify("Aborted. Active mode was required for this action.", severity="warning")
                            return

                        await func(*args, **kwargs)

                    app_.notify("This action requires active mode. Please activate...")
                    await app_.push_screen(Activate(activation_result_callback=_on_activation_result))

            return wrapper

        return decorator

    @on(ScreenSuspend)
    def _post_suspended(self) -> None:
        """
        Notify children widgets that the screen they were mounted on, was suspended.

        Textual lacks a way to notify children widgets that the screen they were mounted on, was suspended.
        This is a workaround.
        """
        self._post_to_children(self, self.Suspended())

    @on(ScreenResume)
    def _post_resumed(self) -> None:
        """Look in the docstring of _post_suspended."""
        self._post_to_children(self, self.Resumed())

    def _post_to_children(self, node: Widget, message: Message) -> None:
        """Post a message to all widgets of the screen (even grandchildren and further)."""
        for child in node.children:
            self._post_to_children(child, message)
            child.post_message(message)

    @staticmethod
    def _sort_bindings(data: ActiveBindingsMap) -> ActiveBindingsMap:
        """
        Sorts bindings by placing the CTRL+X key at first place, then the ESC, then non-fn keys and fn keys at the end of the dictionary.

        This is done so that the bindings in the footer are displayed in a correct, uniform way.

        Args:
        ----
        data: The bindings to sort.

        Returns:
        -------
        New dictionary holding sorted bindings.
        """
        fn_keys = sorted([key for key in data if key.startswith("f")], key=lambda x: int(x[1:]))
        non_fn_keys = [key for key in data if key not in fn_keys]

        # place keys stored in container at the beginning of the list
        container = []
        for key in ("ctrl+x", "escape"):
            if key in non_fn_keys:
                non_fn_keys.remove(key)
                container.append(key)

        sorted_keys = container + non_fn_keys + fn_keys
        return {key: data[key] for key in sorted_keys}

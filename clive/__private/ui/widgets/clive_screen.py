from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, ParamSpec

from textual import on
from textual.events import ScreenResume, ScreenSuspend
from textual.message import Message
from textual.screen import Screen, ScreenResultType

from clive.__private.core.clive_import import get_clive
from clive.__private.core.commands.abc.command_in_active import CommandRequiresActiveModeError
from clive.__private.logger import logger
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from textual.widget import Widget

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
    def prevent_action_when_no_accounts_node_data(func: Callable[P, None]) -> Callable[P, None]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
            app_ = get_clive().app_instance()
            if (
                not app_.world.profile_data.is_accounts_node_data_available
                or not app_.world.profile_data.is_accounts_alarms_data_available
            ):
                logger.debug(f"action {func.__name__} prevented because no node or alarms data is available yet")
                app_.notify("Waiting for data...", severity="warning")
                return
            func(*args, **kwargs)

        return wrapper

    @staticmethod
    def try_again_after_activation(func: Callable[P, Awaitable[None]]) -> Callable[P, Awaitable[None]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
            app_ = get_clive().app_instance()

            try:
                await func(*args, **kwargs)
            except (CommandRequiresActiveModeError, OnlyInActiveModeError):
                from clive.__private.ui.activate.activate import Activate

                async def _on_activation_result(*, activated: bool) -> None:
                    if not activated:
                        app_.notify("Aborted. Active mode was required for this action.", severity="warning")
                        return

                    await func(*args, **kwargs)

                app_.notify("This action requires active mode. Please activate...")
                await app_.push_screen(Activate(activation_result_callback=_on_activation_result))

        return wrapper

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
        Sort bindings in a Clive-way.

        By placing the CTRL+X key first, then the ESC, then non-fn keys and fn keys at the end of the dictionary.
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

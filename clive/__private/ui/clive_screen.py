from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, ParamSpec

from textual import on
from textual.events import ScreenResume, ScreenSuspend
from textual.message import Message
from textual.screen import Screen, ScreenResultType

from clive.__private.core.clive_import import get_clive
from clive.__private.core.commands.abc.command_in_unlocked import CommandRequiresUnlockedModeError
from clive.__private.logger import logger
from clive.__private.ui.clive_widget import CliveWidget
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from textual.widget import Widget

    from clive.__private.ui.app import Clive
    from clive.__private.ui.types import ActiveBindingsMap


P = ParamSpec("P")


class OnlyInUnlockedModeError(CliveError):
    """Should be raised when some action is only available in unlocked mode."""


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

    @classmethod
    def prevent_action_when_no_accounts_node_data(
        cls, message: str = "Waiting for data..."
    ) -> Callable[[Callable[P, None]], Callable[P, None]]:
        def can_run_condition(app: Clive) -> bool:
            accounts = app.world.profile.accounts
            return (
                accounts.is_tracked_accounts_node_data_available and accounts.is_tracked_accounts_alarms_data_available
            )

        return cls._create_prevent_decorator(can_run_condition, message)

    @classmethod
    def prevent_action_when_no_working_account(
        cls, message: str = "Cannot perform this action without working account"
    ) -> Callable[[Callable[P, None]], Callable[P, None]]:
        return cls._create_prevent_decorator(lambda app: app.world.profile.accounts.has_working_account, message)

    @classmethod
    def prevent_action_when_no_tracked_accounts(
        cls, message: str = "Cannot perform this action without tracked accounts"
    ) -> Callable[[Callable[P, None]], Callable[P, None]]:
        return cls._create_prevent_decorator(lambda app: app.world.profile.accounts.has_tracked_accounts, message)

    @staticmethod
    def try_again_after_unlock(func: Callable[P, Awaitable[None]]) -> Callable[P, Awaitable[None]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
            app = get_clive().app_instance()

            try:
                await func(*args, **kwargs)
            except (CommandRequiresUnlockedModeError, OnlyInUnlockedModeError):
                from clive.__private.ui.screens.unlock.unlock import Unlock

                async def _on_unlock_result(*, unlocked: bool) -> None:
                    if not unlocked:
                        app.notify("Aborted. UNLOCKED mode was required for this action.", severity="warning")
                        return

                    await func(*args, **kwargs)

                app.notify("This action requires Clive to be in UNLOCKED mode. Please unlock...")
                await app.push_screen(Unlock(unlock_result_callback=_on_unlock_result))

        return wrapper

    @classmethod
    def _create_prevent_decorator(
        cls, can_run_condition: Callable[[Clive], bool], message: str
    ) -> Callable[[Callable[P, None]], Callable[P, None]]:
        def decorator(func: Callable[P, None]) -> Callable[P, None]:
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
                app = get_clive().app_instance()
                if not can_run_condition(app):
                    logger.debug(f"Preventing action: {func.__name__} with message of: {message}")
                    app.notify(message, severity="warning")
                    return

                func(*args, **kwargs)

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

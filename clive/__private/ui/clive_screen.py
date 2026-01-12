from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, ParamSpec

from textual import on
from textual.events import Mount, ScreenResume, ScreenSuspend
from textual.message import Message
from textual.screen import Screen
from textual.widgets import HelpPanel
from typing_extensions import TypeVar

from clive.__private.core.clive_import import get_clive
from clive.__private.logger import logger
from clive.__private.ui.clive_widget import CliveWidget

if TYPE_CHECKING:
    from collections.abc import Callable

    from textual.widget import Widget

    from clive.__private.ui.app import Clive


P = ParamSpec("P")

ScreenResultT = TypeVar("ScreenResultT", default=None)


class CliveScreen(Screen[ScreenResultT], CliveWidget):
    """
    An ordinary textual screen that also knows what type of application it belongs to.

    Inspired by: https://github.com/Textualize/textual/discussions/1099#discussioncomment-4049612
    """

    class Suspended(Message):
        """Message to notify children widgets that the screen they were mounted on, was suspended."""

    class Resumed(Message):
        """Message to notify children widgets that the screen they were mounted on, was resumed."""

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

    def toggle_help_panel(self, *, show: bool) -> None:
        """
        Toggle the presence of help panel on this screen.

        Args:
            show: Whether to show the help panel.
        """
        query = self.query(HelpPanel)
        is_mounted = bool(query)

        if show and not is_mounted:
            self.mount(HelpPanel())
        else:
            query.remove()

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
    def _handle_screen_resume(self) -> None:
        """Look in the docstring of _post_suspended."""
        self.app.title = f"Clive ({self.__class__.__name__})"
        self._post_to_children(self, self.Resumed())

    @on(Mount)
    def _synchronize_help_panel(self) -> None:
        """Synchronize the presence of help panel on newly created screens."""
        self.toggle_help_panel(show=self.app.is_help_panel_visible)

    @on(Mount)
    def _remove_auto_dismiss_dialogs_from_screen_stack(self) -> None:
        """Remove all AutoDismissDialogs from the screen stack when a new screen is mounted."""
        from clive.__private.ui.dialogs.clive_base_dialogs import AutoDismissDialog  # noqa: PLC0415

        screen_stack = self.app._screen_stacks[self.app._current_mode]
        for screen in list(screen_stack):
            if isinstance(screen, AutoDismissDialog):
                screen_stack.remove(screen)

    def _post_to_children(self, node: Widget, message: Message) -> None:
        """Post a message to all widgets of the screen (even grandchildren and further)."""
        for child in node.children:
            self._post_to_children(child, message)
            child.post_message(message)

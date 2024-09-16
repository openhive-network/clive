from __future__ import annotations

import asyncio
import math
import traceback
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any, TypeVar, cast, overload

from textual import on, work
from textual._context import active_app
from textual.app import App, AutopilotCallbackType
from textual.await_complete import AwaitComplete
from textual.binding import Binding
from textual.events import ScreenResume
from textual.notifications import Notification, Notify, SeverityLevel
from textual.reactive import var

from clive.__private.core.constants.terminal import TERMINAL_HEIGHT, TERMINAL_WIDTH
from clive.__private.core.world import TUIWorld
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.ui.clive_pilot import ClivePilot
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.help import Help
from clive.__private.ui.onboarding.onboarding import Onboarding
from clive.__private.ui.screens.dashboard import Dashboard
from clive.__private.ui.screens.quit import Quit
from clive.exceptions import CommunicationError, ScreenNotFoundError

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Iterator
    from typing import Literal

    from textual.message import Message
    from textual.screen import Screen, ScreenResultCallbackType, ScreenResultType
    from textual.widget import AwaitMount


UpdateScreenResultT = TypeVar("UpdateScreenResultT")


class Clive(App[int]):
    """A singleton instance of the Clive app."""

    from clive import __version__

    SUB_TITLE = __version__

    CSS_PATH = [get_relative_css_path(__file__, name="global")]

    AUTO_FOCUS = "*"

    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("ctrl+s", "app.screenshot()", "Screenshot", show=False),
        Binding("ctrl+x", "push_screen('quit')", "Quit", show=False),
        Binding("c", "clear_notifications", "Clear notifications", show=False),
        Binding("f1", "help", "Help", show=False),
    ]

    SCREENS = {
        "quit": Quit,
        "dashboard": Dashboard,
    }

    header_expanded = var(default=False)
    """Synchronize the expanded header state in all created header objects."""

    notification_history: list[Notification] = var([], init=False)  # type: ignore[assignment]
    """A list of all notifications that were displayed."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._world: TUIWorld | None = None
        self._register_quit_signals()

    @property
    def world(self) -> TUIWorld:
        assert self._world is not None, "World is not set yet."
        return self._world

    @staticmethod
    def app_instance() -> Clive:
        return cast(Clive, active_app.get())

    @classmethod
    def is_launched(cls) -> bool:
        try:
            cls.app_instance()
        except LookupError:
            return False
        return True

    def notify(
        self,
        message: str,
        *,
        title: str = "",
        severity: SeverityLevel = "information",
        timeout: float | None = None,
    ) -> None:
        title = title if title else severity.capitalize()
        timeout = math.inf if timeout is None and severity == "error" else timeout
        return super().notify(message, title=title, severity=severity, timeout=timeout)

    def is_notification_present(self, message: str) -> bool:
        current_notifications = self._notifications
        return any(notification.message == message for notification in current_notifications)

    @on(Notify)
    def _store_notification(self, event: Notify) -> None:
        self.notification_history.append(event.notification)
        self.mutate_reactive(self.__class__.notification_history)  # type: ignore[arg-type]

    @contextmanager
    def suppressed_notifications(self) -> Iterator[None]:
        """Suppress all notifications while in context."""

        def dummy_notify(*_: Any, **__: Any) -> None:
            pass

        old_notify = self.notify
        self.notify = dummy_notify  # type: ignore[method-assign]
        try:
            yield
        finally:
            self.notify = old_notify  # type: ignore[method-assign]

    async def run_async(
        self,
        *,
        headless: bool = False,
        inline: bool = False,
        inline_no_clear: bool = False,
        mouse: bool = True,
        size: tuple[int, int] | None = None,
        auto_pilot: AutopilotCallbackType | None = None,
    ) -> int | None:
        async with TUIWorld() as world:
            self._world = world
            return await super().run_async(
                headless=headless,
                inline=inline,
                inline_no_clear=inline_no_clear,
                mouse=mouse,
                size=size,
                auto_pilot=auto_pilot,
            )

    @asynccontextmanager
    async def run_test(
        self,
        *,
        headless: bool = True,
        size: tuple[int, int] | None = (TERMINAL_WIDTH, TERMINAL_HEIGHT),
        tooltips: bool = False,
        notifications: bool = True,
        message_hook: Callable[[Message], None] | None = None,
    ) -> AsyncGenerator[ClivePilot]:
        async with TUIWorld() as world:
            self._world = world
            async with super().run_test(
                headless=headless,
                size=size,
                tooltips=tooltips,
                notifications=notifications,
                message_hook=message_hook,
            ) as pilot:
                yield cast(ClivePilot, pilot)

    def on_mount(self) -> None:
        def __should_enter_onboarding() -> bool:
            should_force_onboarding = safe_settings.dev.should_force_onboarding
            return self.world.is_in_onboarding_mode or should_force_onboarding

        self.console.set_window_title("Clive")

        self._refresh_node_data_interval = self.set_interval(
            safe_settings.node.refresh_rate_secs, lambda: self.update_data_from_node(), pause=True
        )
        self._refresh_alarms_data_interval = self.set_interval(
            safe_settings.node.refresh_alarms_rate_secs, lambda: self.update_alarms_data(), pause=True
        )

        self.update_data_from_node_asap()
        self.update_alarms_data_asap()

        should_enable_debug_loop = safe_settings.dev.should_enable_debug_loop
        if should_enable_debug_loop:
            debug_loop_period_secs = safe_settings.dev.debug_loop_period_secs
            self.set_interval(debug_loop_period_secs, self.__debug_log)

        if __should_enter_onboarding():
            self.push_screen(Onboarding())
        else:
            self.push_screen(Dashboard())

    @overload
    def push_screen(
        self,
        screen: Screen[ScreenResultType] | str,
        callback: ScreenResultCallbackType[ScreenResultType] | None = None,
        wait_for_dismiss: Literal[False] = False,  # noqa: FBT002
    ) -> AwaitMount: ...

    @overload
    def push_screen(
        self,
        screen: Screen[ScreenResultType] | str,
        callback: ScreenResultCallbackType[ScreenResultType] | None = None,
        wait_for_dismiss: Literal[True] = True,  # noqa: FBT002
    ) -> asyncio.Future[ScreenResultType]: ...

    def push_screen(
        self,
        screen: Screen[ScreenResultType] | str,
        callback: ScreenResultCallbackType[ScreenResultType] | None = None,
        wait_for_dismiss: bool = False,  # noqa: FBT001, FBT002
    ) -> AwaitMount | asyncio.Future[ScreenResultType]:
        fun = super().push_screen
        return self.__update_screen(lambda: fun(screen=screen, callback=callback, wait_for_dismiss=wait_for_dismiss))  # type: ignore[no-any-return, call-overload]

    def pop_screen(self) -> AwaitComplete:
        fun = super().pop_screen
        return self.__update_screen(lambda: fun())

    def pop_screen_until(self, *screens: str | type[Screen[ScreenResultType]]) -> AwaitComplete:
        """
        Pop all screens until one of the given screen is on top of the stack.

        Raises
        ------
        ScreenNotFoundError:  if no screen was found.
        """

        async def _pop_screen_until() -> None:
            for screen in screens:
                if not self.__is_screen_in_stack(screen):
                    continue  # Screen not found, try next one

                with self.batch_update():
                    while not self.__screen_eq(self.screen_stack[-1], screen):
                        with self.prevent(ScreenResume):
                            await self.pop_screen()
                    self.screen.post_message(ScreenResume())
                break  # Screen found and located on top of the stack, stop
            else:
                raise ScreenNotFoundError(
                    f"None of the {screens} screens was found in stack.\nScreen stack: {self.screen_stack}"
                )

        return AwaitComplete(_pop_screen_until()).call_next(self)

    def switch_screen(self, screen: Screen[ScreenResultType] | str) -> AwaitComplete:
        fun = super().switch_screen
        return self.__update_screen(lambda: fun(screen))

    def __update_screen(self, callback: Callable[[], UpdateScreenResultT]) -> UpdateScreenResultT:
        """
        Auxiliary function to override the default push_screen, switch_screen and pop_screen methods.

        Because of Textual's event ScreenResume not being bubbled up, we can't easily hook on it via
        `def on_screen_resume` so we have to override the push_screen, switch_screen and pop_screen methods.
        """
        reply = callback()
        self.title = f"{self.__class__.__name__} ({self.screen.__class__.__name__})"
        return reply

    def action_help(self) -> None:
        self.push_screen(Help())

    def action_screenshot(self, filename: str | None = None, path: str = "./") -> None:
        self.bell()
        path = self.save_screenshot(filename, path)
        message = f"Screenshot saved to [bold green]'{path}'[/]"
        self.notify(message)

    def action_clear_notifications(self) -> None:
        self.clear_notifications()

    def __is_screen_in_stack(self, screen_to_check: str | type[Screen[ScreenResultType]]) -> bool:
        return any(self.__screen_eq(screen, screen_to_check) for screen in self.screen_stack)

    def __screen_eq(self, screen: Screen[ScreenResultType], other: str | type[Screen[ScreenResultType]]) -> bool:
        if isinstance(other, str):
            return screen.__class__.__name__ == other
        return isinstance(screen, other)

    def trigger_profile_watchers(self) -> None:
        self.world.mutate_reactive(TUIWorld.profile)  # type: ignore[arg-type]

    def trigger_node_watchers(self) -> None:
        self.world.mutate_reactive(TUIWorld.node)  # type: ignore[arg-type]

    def trigger_app_state_watchers(self) -> None:
        self.world.mutate_reactive(TUIWorld.app_state)  # type: ignore[arg-type]

    def update_alarms_data_asap(self) -> None:
        """Update alarms as soon as possible after node data becomes available."""

        async def _update_alarms_data_asap() -> None:
            self._refresh_alarms_data_interval.pause()
            while not self.world.profile.accounts.is_tracked_accounts_node_data_available:  # noqa: ASYNC110
                await asyncio.sleep(0.1)
            self.update_alarms_data()
            self._refresh_alarms_data_interval.resume()

        self.run_worker(_update_alarms_data_asap())

    def update_data_from_node_asap(self) -> None:
        self._refresh_node_data_interval.pause()
        self.update_data_from_node()
        self._refresh_node_data_interval.resume()

    @work(name="alarms data update worker")
    async def update_alarms_data(self) -> None:
        accounts = self.world.profile.accounts.tracked
        wrapper = await self.world.commands.update_alarms_data(accounts=accounts)
        if wrapper.error_occurred:
            logger.warning(f"Update alarms data failed: {wrapper.error}")
            return

        self.trigger_profile_watchers()

    @work(name="node data update worker")
    async def update_data_from_node(self) -> None:
        accounts = self.world.profile.accounts.tracked  # accounts list gonna be empty, but dgpo will be refreshed

        wrapper = await self.world.commands.update_node_data(accounts=accounts)
        if wrapper.error_occurred:
            error = wrapper.error
            if isinstance(error, CommunicationError) and not error.is_response_available:
                # notify watchers when node goes offline
                self.trigger_node_watchers()

            logger.warning(f"Update node data failed: {wrapper.error}")
            return

        self.trigger_profile_watchers()
        self.trigger_node_watchers()

    async def __debug_log(self) -> None:
        logger.debug("===================== DEBUG =====================")
        logger.debug(f"Currently focused: {self.focused}")
        logger.debug(f"Screen stack: {self.screen_stack}")

        response = await self.world.node.api.database_api.get_dynamic_global_properties()
        logger.debug(f"Current block: {response.head_block_number}")

        logger.debug("=================================================")

    def _handle_exception(self, error: Exception) -> None:
        # We already had a situation where Textual swallowed an exception without logging it.
        # This is a safeguard to prevent that from happening again.
        logger.error(f"{error.__class__.__name__}: {error}\n{traceback.format_exc()}")
        super()._handle_exception(error)

    def _register_quit_signals(self) -> None:
        import signal

        def callback() -> None:
            self.exit()

        loop = asyncio.get_running_loop()  # can't use self._loop since it's not set yet
        for signal_number in [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM]:
            loop.add_signal_handler(signal_number, callback)

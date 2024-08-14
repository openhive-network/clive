from __future__ import annotations

import asyncio
import math
import traceback
from asyncio import CancelledError
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any, TypeVar, overload

from textual import on, work
from textual._context import active_message_pump
from textual.app import App, AutopilotCallbackType
from textual.binding import Binding
from textual.events import ScreenResume
from textual.notifications import Notification, Notify, SeverityLevel
from textual.reactive import var

from clive.__private.core.constants.terminal import TERMINAL_HEIGHT, TERMINAL_WIDTH
from clive.__private.core.world import TextualWorld
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.ui.dashboard.dashboard_locked import DashboardLocked
from clive.__private.ui.dashboard.dashboard_unlocked import DashboardUnlocked
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.manual_reactive import ManualReactive
from clive.__private.ui.onboarding.onboarding import Onboarding
from clive.__private.ui.quit.quit import Quit
from clive.__private.ui.shared.help import Help
from clive.exceptions import ScreenNotFoundError

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Iterator
    from typing import ClassVar, Literal

    from textual.message import Message
    from textual.screen import Screen, ScreenResultCallbackType, ScreenResultType
    from textual.widget import AwaitMount

    from clive.__private.ui.pilot import ClivePilot

UpdateScreenResultT = TypeVar("UpdateScreenResultT")


class Clive(App[int], ManualReactive):
    """A singleton instance of the Clive app."""

    from clive import __version__

    SUB_TITLE = __version__

    CSS_PATH = [get_relative_css_path(__file__, name="global")]

    AUTO_FOCUS = "*"

    BINDINGS = [
        Binding("ctrl+s", "app.screenshot()", "Screenshot", show=False),
        Binding("ctrl+x", "push_screen('quit')", "Quit", show=False),
        Binding("c", "clear_notifications", "Clear notifications", show=False),
        Binding("f1", "help", "Help", show=False),
    ]

    SCREENS = {
        "quit": Quit,
        "dashboard_locked": DashboardLocked,
        "dashboard_unlocked": DashboardUnlocked,
    }

    header_expanded = var(default=False)
    """Synchronize the expanded header state in all created header objects."""

    __app_instance: ClassVar[Clive | None] = None
    """The singleton instance of the Clive app."""

    is_launched: ClassVar[bool] = False
    """Whether the Clive app is currently launched."""

    world: ClassVar[TextualWorld] = None  # type: ignore[assignment]

    notification_history: list[Notification] = var([], init=False)  # type: ignore[assignment]
    """A list of all notifications that were displayed."""

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
        self.update_reactive("notification_history")

    @contextmanager
    def suppressed_notifications(self) -> Iterator[None]:
        """Suppress all notifications while in context."""

        def dummy_notify(
            message: str,  # noqa: ARG001
            *,
            title: str = "",  # noqa: ARG001
            severity: SeverityLevel = "information",  # noqa: ARG001
            timeout: float | None = None,  # noqa: ARG001
        ) -> None:
            return

        old_notify = self.notify
        self.notify = dummy_notify  # type: ignore[method-assign]
        yield
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
        try:
            async with TextualWorld() as world:
                self.__class__.world = world
                return await super().run_async(
                    headless=headless,
                    inline=inline,
                    inline_no_clear=inline_no_clear,
                    mouse=mouse,
                    size=size,
                    auto_pilot=auto_pilot,
                )
        except CancelledError:
            pass
        finally:
            self.__cleanup()
        return 1

    @asynccontextmanager
    async def run_test(
        self,
        *,
        headless: bool = True,
        size: tuple[int, int] | None = (TERMINAL_WIDTH, TERMINAL_HEIGHT),
        tooltips: bool = False,
        notifications: bool = True,
        message_hook: Callable[[Message], None] | None = None,
    ) -> AsyncGenerator[ClivePilot, None]:
        try:
            async with TextualWorld() as world:
                self.__class__.world = world
                async with super().run_test(
                    headless=headless,
                    size=size,
                    tooltips=tooltips,
                    notifications=notifications,
                    message_hook=message_hook,
                ) as pilot:
                    yield pilot  # type: ignore[misc]
        finally:
            self.__cleanup()

    def on_mount(self) -> None:
        def __should_enter_onboarding() -> bool:
            should_force_onboarding = safe_settings.dev.should_force_onboarding
            return self.world.profile.name == Onboarding.ONBOARDING_PROFILE_NAME or should_force_onboarding

        self.__class__.is_launched = True
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
            self.push_screen(DashboardLocked())

    def replace_screen(
        self, old: str | type[Screen[ScreenResultType]], new: str | Screen[ScreenResultType]
    ) -> AwaitMount:
        new_, _ = self._get_screen(new)

        if self.is_screen_on_top(old):
            return self.switch_screen(new_)

        old_screen_index = self.__get_screen_index(old)
        self.app._screen_stack.pop(old_screen_index)
        return self.push_screen_at(old_screen_index, new_)

    def __get_screen_index(self, screen: str | type[Screen[ScreenResultType]]) -> int:
        for index, screen_on_stack in enumerate(self.app._screen_stack):
            if self.__screen_eq(screen_on_stack, screen):
                return index

        raise ScreenNotFoundError(f"Screen {screen} is not in the screen stack.\nScreen stack: {self.screen_stack}")

    def is_screen_on_top(self, screen: str | type[Screen[Any]]) -> bool:
        return self.__screen_eq(self.screen, screen)

    @overload
    def push_screen(  # type: ignore[overload-overlap]
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

    def push_screen_at(
        self,
        index: int,
        screen: Screen[ScreenResultType] | str,
        callback: ScreenResultCallbackType[ScreenResultType] | None = None,
    ) -> AwaitMount:
        """Push a screen at the given index in the stack."""
        next_screen, await_mount = self.app._get_screen(screen)

        try:
            message_pump = active_message_pump.get()
        except LookupError:
            message_pump = self.app

        next_screen._push_result_callback(message_pump, callback)
        self._load_screen_css(next_screen)
        self.app._screen_stack.insert(index, next_screen)
        return await_mount

    def pop_screen(self) -> Screen[Any]:
        fun = super().pop_screen
        return self.__update_screen(lambda: fun())

    def pop_screen_until(self, *screens: str | type[Screen[ScreenResultType]]) -> None:
        """
        Pop all screens until one of the given screen is on top of the stack.

        Raises
        ------
        ScreenNotFoundError:  if no screen was found.
        """
        for screen in screens:
            if not self.__is_screen_in_stack(screen):
                continue  # Screen not found, try next one

            with self.batch_update():
                while not self.__screen_eq(self.screen_stack[-1], screen):
                    with self.prevent(ScreenResume):
                        self.pop_screen()
                self.screen.post_message(ScreenResume())
            break  # Screen found and located on top of the stack, stop
        else:
            raise ScreenNotFoundError(
                f"None of the {screens} screens was found in stack.\nScreen stack: {self.screen_stack}"
            )

    def switch_screen(self, screen: Screen[ScreenResultType] | str) -> AwaitMount:
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

    def post_message_to_everyone(self, message: Message) -> None:
        """Post a message to all screens in the stack."""
        for screen in reversed(self.screen_stack):
            screen.post_message(message)

    def post_message_to_screen(self, screen: str | type[Screen[ScreenResultType]], message: Message) -> None:
        """Post a message to a specific screen in the stack."""
        self.__assert_screen_in_stack(screen)
        for screen_ in reversed(self.screen_stack):
            if self.__screen_eq(screen_, screen):
                screen_.post_message(message)

    def __assert_screen_in_stack(self, screen_to_check: str | type[Screen[ScreenResultType]]) -> None:
        if not self.__is_screen_in_stack(screen_to_check):
            raise ScreenNotFoundError(
                f"Screen {screen_to_check} is not in the screen stack.\nScreen stack: {self.screen_stack}"
            )

    def __is_screen_in_stack(self, screen_to_check: str | type[Screen[ScreenResultType]]) -> bool:
        return any(self.__screen_eq(screen, screen_to_check) for screen in self.screen_stack)

    def __screen_eq(self, screen: Screen[ScreenResultType], other: str | type[Screen[ScreenResultType]]) -> bool:
        if isinstance(other, str):
            return screen.__class__.__name__ == other
        return isinstance(screen, other)

    def trigger_profile_watchers(self) -> None:
        self.world.update_reactive("profile")

    def trigger_node_watchers(self) -> None:
        self.world.update_reactive("node")

    def trigger_app_state_watchers(self) -> None:
        self.world.update_reactive("app_state")

    def update_alarms_data_asap(self) -> None:
        """Update alarms as soon as possible after node data becomes available."""

        async def _update_alarms_data_asap() -> None:
            self._refresh_alarms_data_interval.pause()
            while not self.world.profile.accounts.is_tracked_accounts_node_data_available:
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

    @classmethod
    def is_app_exist(cls) -> bool:
        return cls.__app_instance is not None

    @classmethod
    def app_instance(cls) -> Clive:
        if not cls.is_app_exist():
            cls.__app_instance = Clive()
        assert cls.__app_instance is not None
        return cls.__app_instance

    def _handle_exception(self, error: Exception) -> None:
        # We already had a situation where Textual swallowed an exception without logging it.
        # This is a safeguard to prevent that from happening again.
        logger.error(f"{error.__class__.__name__}: {error}\n{traceback.format_exc()}")
        self.__cleanup()
        super()._handle_exception(error)

    def __cleanup(self) -> None:
        logger.debug("Cleaning up...")
        self.__class__.is_launched = False
        self.__class__.world = None  # type: ignore[assignment]
        self.__class__.__app_instance = None

from __future__ import annotations

import asyncio
import contextlib
import math
import traceback
from asyncio import CancelledError
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any, TypeVar, overload

from textual import work
from textual._context import active_message_pump
from textual.app import App, AutopilotCallbackType
from textual.binding import Binding
from textual.notifications import Notification, SeverityLevel
from textual.reactive import reactive, var

from clive.__private.config import settings
from clive.__private.core.profile_data import NoWorkingAccountError, ProfileData
from clive.__private.core.world import TextualWorld
from clive.__private.logger import logger
from clive.__private.ui.dashboard.dashboard_active import DashboardActive
from clive.__private.ui.dashboard.dashboard_inactive import DashboardInactive
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.manual_reactive import ManualReactive
from clive.__private.ui.onboarding.onboarding import Onboarding
from clive.__private.ui.quit.quit import Quit
from clive.__private.ui.shared.help import Help
from clive.__private.ui.terminal.command_line import CommandLinePrompt
from clive.__private.ui.terminal.terminal_screen import TerminalScreen
from clive.exceptions import ScreenNotFoundError

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Iterator
    from typing import ClassVar, Literal

    from rich.console import RenderableType
    from textual.message import Message
    from textual.pilot import Pilot
    from textual.screen import Screen, ScreenResultCallbackType, ScreenResultType
    from textual.widget import AwaitMount

    from clive.__private.storage.accounts import Account
    from clive.__private.ui.types import NamespaceBindingsMapType

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
        "dashboard_inactive": DashboardInactive,
        "dashboard_active": DashboardActive,
    }

    header_expanded = var(False)
    """Synchronize the expanded header state in all created header objects."""

    __app_instance: ClassVar[Clive | None] = None
    """The singleton instance of the Clive app."""

    is_launched: ClassVar[bool] = False
    """Whether the Clive app is currently launched."""

    world: ClassVar[TextualWorld] = None  # type: ignore

    logs: list[RenderableType | object] = reactive([], repaint=False, init=False, always_update=True)  # type: ignore[assignment]
    """A list of all log messages. Shared between all Terminal.Logs widgets."""

    @property
    def namespace_bindings(self) -> NamespaceBindingsMapType:
        """Provides the ability to control the binding order in the footer."""
        return self.__sort_bindings(super().namespace_bindings)

    def notify(
        self,
        message: str,
        *,
        title: str = "",
        severity: SeverityLevel = "information",
        timeout: float = Notification.timeout,
    ) -> None:
        title = title if title else severity.capitalize()
        timeout = math.inf if timeout == Notification.timeout and severity == "error" else timeout
        return super().notify(message, title=title, severity=severity, timeout=timeout)

    @contextmanager
    def suppressed_notifications(self) -> Iterator[None]:
        """Suppress all notifications while in context."""

        def dummy_notify(
            message: str,  # noqa: ARG001
            *,
            title: str = "",  # noqa: ARG001
            severity: SeverityLevel = "information",  # noqa: ARG001
            timeout: float = Notification.timeout,  # noqa: ARG001
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
        size: tuple[int, int] | None = None,
        auto_pilot: AutopilotCallbackType | None = None,
    ) -> int | None:
        try:
            async with TextualWorld() as world:
                self.__class__.world = world
                return await super().run_async(headless=headless, size=size, auto_pilot=auto_pilot)
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
        size: tuple[int, int] | None = (132, 24),
        tooltips: bool = False,
        notifications: bool = True,
        message_hook: Callable[[Message], None] | None = None,
    ) -> AsyncGenerator[Pilot[int], None]:
        async with super().run_test(
            headless=headless, size=size, tooltips=tooltips, notifications=notifications, message_hook=message_hook
        ) as pilot:
            yield pilot
        self.__cleanup()

    def on_mount(self) -> None:
        def __should_enter_onboarding() -> bool:
            return self.world.profile_data.name == ProfileData.ONBOARDING_PROFILE_NAME or settings.FORCE_ONBOARDING

        self.__class__.is_launched = True
        self.__amount_of_fails_during_update_node_data = 0
        self.console.set_window_title("Clive")

        self.set_interval(settings.get("node.refresh_rate", 1.5), lambda: self.update_data_from_node())

        if settings.LOG_DEBUG_LOOP:
            self.set_interval(settings.get("LOG_DEBUG_PERIOD", 1), self.__debug_log)

        if __should_enter_onboarding():
            self.push_screen(Onboarding())
        else:
            self.push_screen(DashboardInactive())

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
    def push_screen(  # type: ignore[misc]
        self,
        screen: Screen[ScreenResultType] | str,
        callback: ScreenResultCallbackType[ScreenResultType] | None = None,
        wait_for_dismiss: Literal[False] = False,
    ) -> AwaitMount:
        ...

    @overload
    def push_screen(
        self,
        screen: Screen[ScreenResultType] | str,
        callback: ScreenResultCallbackType[ScreenResultType] | None = None,
        wait_for_dismiss: Literal[True] = True,
    ) -> asyncio.Future[ScreenResultType]:
        ...

    def push_screen(
        self,
        screen: Screen[ScreenResultType] | str,
        callback: ScreenResultCallbackType[ScreenResultType] | None = None,
        wait_for_dismiss: bool = False,
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
                    self.pop_screen()
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

    def action_terminal(self) -> None:
        self.push_screen(TerminalScreen())

    def action_help(self) -> None:
        self.push_screen(Help())

    def action_screenshot(self, filename: str | None = None, path: str = "./") -> None:
        self.bell()
        path = self.save_screenshot(filename, path)
        message = f"Screenshot saved to [bold green]'{path}'[/]"
        self.notify(message)

    def action_clear_notifications(self) -> None:
        self.clear_notifications()

    async def write(
        self, text: RenderableType, *, message_type: Literal["info", "warning", "input"] | None = None
    ) -> None:
        if message_type == "info":
            text = f"[blue]INFO:[/blue] {text}"
        elif message_type == "input":
            prefix = await self.query(CommandLinePrompt).first(CommandLinePrompt).get_current_prompt()
            text = f"{prefix} {text}"

        self.logs += [text]

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

    def trigger_profile_data_watchers(self) -> None:
        self.world.update_reactive("profile_data")

    def trigger_node_watchers(self) -> None:
        self.world.update_reactive("node")

    def trigger_app_state_watchers(self) -> None:
        self.world.update_reactive("app_state")

    @staticmethod
    def __sort_bindings(data: NamespaceBindingsMapType) -> NamespaceBindingsMapType:
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

    @work(name="node data update worker")
    async def update_data_from_node(self) -> None:
        allowed_fails_of_update_node_data = 5
        accounts: list[Account] = []  # accounts list gonna be empty, but dgpo will be refreshed
        with contextlib.suppress(NoWorkingAccountError):
            accounts.append(self.world.profile_data.working_account)
        accounts.extend(self.world.profile_data.watched_accounts)

        try:
            await self.world.commands.update_node_data(accounts=accounts)
            self.__amount_of_fails_during_update_node_data = 0
        except Exception as error:  # noqa: BLE001
            self.__amount_of_fails_during_update_node_data += 1
            logger.warning(f"Update node data failed {self.__amount_of_fails_during_update_node_data} times: {error}")
            if self.__amount_of_fails_during_update_node_data >= allowed_fails_of_update_node_data:
                raise
        else:
            self.trigger_profile_data_watchers()
            self.trigger_app_state_watchers()

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

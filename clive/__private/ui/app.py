from __future__ import annotations

import contextlib
import math
import traceback
from datetime import timedelta
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, Any, Final, TypeVar

from textual import on, work
from textual.app import App, AutopilotCallbackType
from textual.binding import Binding
from textual.notifications import Notification, SeverityLevel
from textual.reactive import reactive, var

from clive.__private.config import settings
from clive.__private.core.communication import Communication
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.raise_exception_helper import RaiseExceptionHelper
from clive.__private.core.world import TextualWorld
from clive.__private.logger import logger
from clive.__private.ui.app_messages import ProfileDataUpdated
from clive.__private.ui.background_tasks import BackgroundErrorOccurred, BackgroundTasks
from clive.__private.ui.dashboard.dashboard_active import DashboardActive
from clive.__private.ui.dashboard.dashboard_inactive import DashboardInactive
from clive.__private.ui.manual_reactive import ManualReactive
from clive.__private.ui.onboarding.onboarding import Onboarding
from clive.__private.ui.quit.quit import Quit
from clive.__private.ui.shared.help import Help
from clive.__private.ui.terminal.command_line import CommandLinePrompt
from clive.__private.ui.terminal.terminal_screen import TerminalScreen
from clive.exceptions import ScreenNotFoundError
from clive.version import VERSION_INFO

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import ClassVar, Literal

    from rich.console import RenderableType
    from textual.message import Message
    from textual.screen import Screen, ScreenResultCallbackType, ScreenResultType
    from textual.widget import AwaitMount

    from clive.__private.ui.app_messages import NodeDataUpdated
    from clive.__private.ui.types import NamespaceBindingsMapType

UpdateScreenResultT = TypeVar("UpdateScreenResultT")


class Clive(App[int], ManualReactive):
    """A singleton instance of the Clive app."""

    SUB_TITLE = VERSION_INFO

    CSS_PATH = list(Path(__file__).parent.glob("**/*.scss"))

    BINDINGS = [
        Binding("ctrl+s", "app.screenshot()", "Screenshot", show=False),
        Binding("l", "mock_log", "Mock log", show=False),
        Binding("ctrl+x", "push_screen('quit')", "Quit"),
        Binding("f1", "help", "Help"),
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
    ) -> Notification:
        title = title if title else severity.capitalize()
        timeout = math.inf if timeout == Notification.timeout and severity == "error" else timeout
        return super().notify(message, title=title, severity=severity, timeout=timeout)

    def run(
        self,
        *,
        headless: bool = False,
        size: tuple[int, int] | None = None,
        auto_pilot: AutopilotCallbackType | None = None,
    ) -> int | None:
        try:
            return super().run(headless=headless, size=size, auto_pilot=auto_pilot)
        finally:
            self.__cleanup()

    def on_mount(self) -> None:
        self.__class__.is_launched = True
        self.mount(self.world)
        self.console.set_window_title("Clive")
        RaiseExceptionHelper.initialize()

        def __should_enter_onboarding() -> bool:
            return self.world.profile_data.name == ProfileData.ONBOARDING_PROFILE_NAME or settings.FORCE_ONBOARDING

        self.background_tasks = BackgroundTasks(exception_handler=self.__handle_background_error)
        self.background_tasks.run_every(timedelta(seconds=1.5), self.__update_data_from_node)
        self.set_interval(1, self.check_if_should_deactivate)  # type: ignore[arg-type]
        if settings.LOG_DEBUG_LOOP:
            self.background_tasks.run_every(timedelta(seconds=1), self.__debug_log)

        if __should_enter_onboarding():
            self.push_screen(Onboarding())
        else:
            self.push_screen(DashboardInactive())

    def replace_screen(self, old: str | type[Screen[ScreenResultType]], new: str | Screen[ScreenResultType]) -> None:
        new_, _ = self._get_screen(new)

        if self.is_screen_on_top(old):
            self.switch_screen(new_)
            return

        old_screen_index = self.__get_screen_index(old)
        self.app._screen_stack.pop(old_screen_index)
        self.push_screen_at(old_screen_index, new_)

    def __get_screen_index(self, screen: str | type[Screen[ScreenResultType]]) -> int:
        for index, screen_on_stack in enumerate(self.app._screen_stack):
            if self.__screen_eq(screen_on_stack, screen):
                return index

        raise ScreenNotFoundError(f"Screen {screen} is not in the screen stack.\nScreen stack: {self.screen_stack}")

    def is_screen_on_top(self, screen: str | type[Screen[Any]]) -> bool:
        return self.__screen_eq(self.screen, screen)

    def push_screen(
        self,
        screen: Screen[ScreenResultType] | str,
        callback: ScreenResultCallbackType[ScreenResultType] | None = None,
    ) -> AwaitMount:
        fun = super().push_screen
        return self.__update_screen(lambda: fun(screen, callback))

    def push_screen_at(
        self,
        index: int,
        screen: Screen[ScreenResultType] | str,
        callback: ScreenResultCallbackType[ScreenResultType] | None = None,
    ) -> None:
        """Push a screen at the given index in the stack."""
        screen_, _ = self.app._get_screen(screen)
        screen_._push_result_callback(self.screen if self._screen_stack else None, callback)
        self.app._screen_stack.insert(index, screen_)

    def pop_screen(self) -> Screen[Any]:
        fun = super().pop_screen
        return self.__update_screen(lambda: fun())

    @work(
        name="Inactive state guarantor",
        description="Checks if should deactivate TUI after beekeeper notification about closing wallets",
    )
    async def check_if_should_deactivate(self) -> None:
        """
        Ensures that TUI is in the INACTIVE mode after beekeeper notification about closing wallets is received.

        This is a workaround, because we re unable to run some actions on the TUI application in
        TextualWorld.notify_wallet_closing, because it is called from NotificationServer thread and not from
        the TUI thread. It might be possible to do it in the mentioned place if NotificationServer will be able
        to run async.
        """
        if self.world.app_state.is_active:
            return

        if not self.world.app_state.is_deactivation_pending:
            return

        self.world.app_state.is_deactivation_pending = False

        with contextlib.suppress(ScreenNotFoundError):
            self.replace_screen("DashboardActive", "dashboard_inactive")

        self.notify("Switched to the INACTIVE mode.", severity="warning", timeout=5)
        self.world.update_reactive("app_state")

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

    def action_mock_log(self) -> None:
        self.write("This is a mock log.", message_type="info")

    def action_help(self) -> None:
        self.push_screen(Help(self.screen))

    def action_screenshot(self, filename: str | None = None, path: str = "./") -> None:
        self.bell()
        path = self.save_screenshot(filename, path)
        message = f"Screenshot saved to [bold green]'{path}'[/]"
        self.notify(message)

    def write(self, text: RenderableType, *, message_type: Literal["info", "warning", "input"] | None = None) -> None:
        if message_type == "info":
            text = f"[blue]INFO:[/blue] {text}"
        elif message_type == "input":
            prefix = self.query(CommandLinePrompt).first(CommandLinePrompt).get_current_prompt()
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

    @on(BackgroundErrorOccurred)
    def background_error_occurred(self, event: BackgroundErrorOccurred) -> None:
        raise event.exception

    @on(ProfileDataUpdated)
    def profile_data_updated(self) -> None:
        self.world.update_reactive("profile_data")

    def on_node_data_updated(self, _: NodeDataUpdated) -> None:
        self.world.update_reactive("node")

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

    def __handle_background_error(self, error: Exception) -> None:
        self.post_message(BackgroundErrorOccurred(error))

    async def __update_data_from_node(self) -> None:
        accounts = [self.world.profile_data.working_account, *self.world.profile_data.watched_accounts]

        try:
            await self.world.commands.update_node_data(accounts=accounts)
        except Exception as error:  # noqa: BLE001
            RaiseExceptionHelper.raise_exception_in_main_thread(error)
        else:
            self.world.update_reactive("profile_data")
            self.world.update_reactive("app_state")

    async def __debug_log(self) -> None:
        logger.debug("===================== DEBUG =====================")
        logger.debug(f"Currently focused: {self.focused}")
        logger.debug(f"Screen stack: {self.screen_stack}")
        logger.debug(f"Background tasks: { {name: task._state for name, task in self.background_tasks.tasks.items()} }")

        query = {"jsonrpc": "2.0", "method": "database_api.get_dynamic_global_properties", "id": 1}
        response = await Communication.arequest(str(self.world.profile_data.node_address), data=query)
        result = response.json()
        logger.debug(f'Current block: {result["result"]["head_block_number"]}')

        logger.debug("=================================================")

    @classmethod
    def is_app_exist(cls) -> bool:
        return cls.__app_instance is not None

    @classmethod
    def app_instance(cls) -> Clive:
        if not cls.is_app_exist():
            cls.world = TextualWorld()
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
        self.__class__.is_launched = False
        self.world.close()

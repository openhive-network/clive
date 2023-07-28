from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, overload

from textual.app import App, AutopilotCallbackType
from textual.binding import Binding
from textual.reactive import reactive, var

from clive.__private.config import settings
from clive.__private.core.communication import Communication
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.raise_exception_helper import RaiseExceptionHelper
from clive.__private.core.world import TextualWorld
from clive.__private.logger import logger
from clive.__private.ui.background_tasks import BackgroundErrorOccurred, BackgroundTasks
from clive.__private.ui.dashboard.dashboard_active import DashboardActive
from clive.__private.ui.dashboard.dashboard_inactive import DashboardInactive
from clive.__private.ui.manual_reactive import ManualReactive
from clive.__private.ui.onboarding.onboarding import Onboarding
from clive.__private.ui.quit.quit import Quit
from clive.__private.ui.shared.help import Help
from clive.__private.ui.terminal.command_line import CommandLinePrompt
from clive.__private.ui.terminal.terminal_screen import TerminalScreen
from clive.__private.ui.widgets.notification import Notification
from clive.exceptions import ScreenNotFoundError
from clive.version import VERSION_INFO

if TYPE_CHECKING:
    from typing import ClassVar, Literal

    from rich.console import RenderableType
    from textual.message import Message
    from textual.screen import Screen
    from textual.widget import AwaitMount

    from clive.__private.core.commands.command_wrappers import CommandWrapper
    from clive.__private.ui.app_messages import NodeDataUpdated, ProfileDataUpdated
    from clive.__private.ui.types import NamespaceBindingsMapType


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

    def run(
        self,
        *,
        headless: bool = False,
        size: tuple[int, int] | None = None,
        auto_pilot: AutopilotCallbackType | None = None,
    ) -> int | None:
        try:
            self.__class__.is_launched = True
            return super().run(headless=headless, size=size, auto_pilot=auto_pilot)
        finally:
            self.__cleanup()

    def on_mount(self) -> None:
        self.console.set_window_title("Clive")
        RaiseExceptionHelper.initialize()

        def __should_enter_onboarding() -> bool:
            return self.world.profile_data.name == ProfileData.ONBOARDING_PROFILE_NAME

        self.background_tasks = BackgroundTasks(exception_handler=self.__handle_background_error)
        self.__amount_of_fails_during_update_node_data = 0
        self.background_tasks.run_every(timedelta(seconds=1.5), self.__update_data_from_node)
        if settings.LOG_DEBUG_LOOP:
            self.background_tasks.run_every(timedelta(seconds=1), self.__debug_log)

        self.push_screen(DashboardInactive())
        if __should_enter_onboarding():
            self.push_screen(Onboarding())

    def replace_screen(self, old: str | type[Screen], new: str | Screen) -> None:
        new_, _ = self._get_screen(new)

        if self.is_screen_on_top(old):
            self.switch_screen(new_)
            return

        old_screen_index = self.__get_screen_index(old)
        self.app._screen_stack.pop(old_screen_index)
        self.push_screen_at(old_screen_index, new_)

    def __get_screen_index(self, screen: str | type[Screen]) -> int:
        for index, screen_on_stack in enumerate(self.app._screen_stack):
            if self.__screen_eq(screen_on_stack, screen):
                return index

        raise ScreenNotFoundError(f"Screen {screen} is not in the screen stack.\nScreen stack: {self.screen_stack}")

    def is_screen_on_top(self, screen: str | type[Screen]) -> bool:
        return self.__screen_eq(self.screen, screen)

    def push_screen(self, screen: Screen | str) -> AwaitMount:
        return self.__update_screen("push_screen", screen)

    def push_screen_at(self, index: int, screen: Screen | str) -> None:
        """Push a screen at the given index in the stack."""
        screen_, _ = self.app._get_screen(screen)
        self.app._screen_stack.insert(index, screen_)

    def pop_screen(self) -> Screen:
        return self.__update_screen("pop_screen")

    def pop_screen_until(self, *screens: str | type[Screen]) -> None:
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

    def switch_screen(self, screen: Screen | str) -> AwaitMount:
        return self.__update_screen("switch_screen", screen)

    @overload
    def __update_screen(self, method_name: Literal["push_screen", "switch_screen"], screen: Screen | str) -> AwaitMount:
        ...

    @overload
    def __update_screen(self, method_name: Literal["pop_screen"]) -> Screen:
        ...

    def __update_screen(
        self, method_name: Literal["push_screen", "switch_screen", "pop_screen"], screen: str | Screen | None = None
    ) -> AwaitMount | Screen:
        """
        Auxiliary function to override the default push_screen, switch_screen and pop_screen methods.

        Because of Textual's event ScreenResume not being bubbled up, we can't easily hook on it via
        `def on_screen_resume` so we have to override the push_screen, switch_screen and pop_screen methods.
        """
        method = getattr(super(), method_name)
        reply: AwaitMount | Screen = method(screen) if screen else method()

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
        Notification(message).show()

    def write(self, text: RenderableType, *, message_type: Literal["info", "warning", "input"] | None = None) -> None:
        if message_type == "info":
            text = f"[blue]INFO:[/blue] {text}"
        elif message_type == "input":
            prefix = self.query(CommandLinePrompt).first(CommandLinePrompt).get_current_prompt()
            text = f"{prefix} {text}"

        self.logs += [text]

    def activate(self, password: str, active_mode_time: timedelta | None = None) -> CommandWrapper:
        if active_mode_time is not None:
            self.world.commands.set_timeout(seconds=int(active_mode_time.total_seconds()))
        wrapper = self.world.commands.activate(password=password, time=active_mode_time)
        self.world.update_reactive("app_state")
        return wrapper

    def deactivate(self) -> None:
        self.world.commands.deactivate()
        self.world.update_reactive("app_state")
        self.switch_screen("dashboard_inactive")

    def post_message_to_everyone(self, message: Message) -> None:
        """Post a message to all screens in the stack."""
        for screen in reversed(self.screen_stack):
            screen.post_message(message)

    def post_message_to_screen(self, screen: str | type[Screen], message: Message) -> None:
        """Post a message to a specific screen in the stack."""
        self.__assert_screen_in_stack(screen)
        for screen_ in reversed(self.screen_stack):
            if self.__screen_eq(screen_, screen):
                screen_.post_message(message)

    def __assert_screen_in_stack(self, screen_to_check: str | type[Screen]) -> None:
        if not self.__is_screen_in_stack(screen_to_check):
            raise ScreenNotFoundError(
                f"Screen {screen_to_check} is not in the screen stack.\nScreen stack: {self.screen_stack}"
            )

    def __is_screen_in_stack(self, screen_to_check: str | type[Screen]) -> bool:
        return any(self.__screen_eq(screen, screen_to_check) for screen in self.screen_stack)

    def __screen_eq(self, screen: Screen, other: str | type[Screen]) -> bool:
        if isinstance(other, str):
            return screen.__class__.__name__ == other
        return isinstance(screen, other)

    def on_background_error_occurred(self, event: BackgroundErrorOccurred) -> None:
        raise event.exception

    def on_profile_data_updated(self, _: ProfileDataUpdated) -> None:
        self.world.update_reactive("profile_data")

    def on_node_data_updated(self, _: NodeDataUpdated) -> None:
        self.world.update_reactive("node")

    @staticmethod
    def __sort_bindings(data: NamespaceBindingsMapType) -> NamespaceBindingsMapType:
        """
        Sorts bindings by placing the ESC key at first place and fn keys at the end of the dictionary.

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

        # place ESC key before other non-fn keys
        if "escape" in non_fn_keys:
            non_fn_keys.remove("escape")
            non_fn_keys.insert(0, "escape")

        sorted_keys = non_fn_keys + fn_keys
        return {key: data[key] for key in sorted_keys}

    def __handle_background_error(self, error: Exception) -> None:
        self.post_message(BackgroundErrorOccurred(error))

    async def __update_data_from_node(self) -> None:
        allowed_fails_of_update_node_data = 5
        accounts = [self.world.profile_data.working_account, *self.world.profile_data.watched_accounts]

        try:
            await self.world.commands.update_node_data(accounts=accounts)
            self.__amount_of_fails_during_update_node_data = 0
        except Exception as error:  # noqa: BLE001
            self.__amount_of_fails_during_update_node_data += 1
            logger.warning(f"Update node data failed {self.__amount_of_fails_during_update_node_data} times: {error}")
            if self.__amount_of_fails_during_update_node_data >= allowed_fails_of_update_node_data:
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
        response = await Communication.arequest(str(self.world.node.address), data=query)
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
        logger.error(str(error))
        self.__cleanup()
        super()._handle_exception(error)

    def __cleanup(self) -> None:
        self.__class__.is_launched = False
        self.world.close()

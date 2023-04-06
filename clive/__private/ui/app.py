from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, overload

from textual.app import App
from textual.binding import Binding
from textual.reactive import reactive, var

from clive.__private.config import settings
from clive.__private.core.commands.activate import Activate
from clive.__private.core.commands.deactivate import Deactivate
from clive.__private.core.communication import Communication
from clive.__private.core.world import World
from clive.__private.logger import logger
from clive.__private.ui.activate.activate import Activate as ActivateScreen
from clive.__private.ui.background_tasks import BackgroundErrorOccurred, BackgroundTasks
from clive.__private.ui.dashboard.dashboard_active import DashboardActive
from clive.__private.ui.dashboard.dashboard_inactive import DashboardInactive
from clive.__private.ui.onboarding.onboarding import Onboarding
from clive.__private.ui.quit.quit import Quit
from clive.__private.ui.shared.help import Help
from clive.__private.ui.terminal.command_line import CommandLinePrompt
from clive.__private.ui.terminal.terminal_screen import TerminalScreen
from clive.__private.ui.widgets.notification import Notification
from clive.exceptions import ScreenNotFoundError
from clive.version import VERSION_INFO

if TYPE_CHECKING:
    from collections.abc import Callable

    from rich.console import RenderableType
    from textual.message import Message
    from textual.screen import Screen
    from textual.widget import AwaitMount

    from clive.__private.core.app_state import AppState
    from clive.__private.core.profile_data import ProfileData
    from clive.__private.storage.mock_database import NodeData
    from clive.__private.ui.app_messages import ProfileDataUpdated
    from clive.__private.ui.types import NamespaceBindingsMapType


class Clive(App[int]):
    """A singleton instance of the Clive app."""

    SUB_TITLE = VERSION_INFO

    CSS_PATH = list(Path(__file__).parent.glob("**/*.scss"))

    BINDINGS = [
        Binding("ctrl+c", "push_screen('quit')", "Quit", show=False),
        Binding("ctrl+s", "app.screenshot()", "Screenshot", show=False),
        Binding("l", "mock_log", "Mock log", show=False),
        Binding("f1", "help", "Help"),
    ]

    SCREENS = {
        "quit": Quit,
        "dashboard_inactive": DashboardInactive,
        "dashboard_active": DashboardActive,
    }

    header_expanded = var(False)
    """Synchronize the expanded header state in all created header objects."""

    world = World()
    node_data: NodeData = var(world.node_data)  # type: ignore[assignment]
    profile_data: ProfileData = var(world.profile_data)  # type: ignore[assignment]
    app_state: AppState = var(world.app_state)  # type: ignore[assignment]

    logs: list[RenderableType | object] = reactive([], repaint=False, init=False, always_update=True)  # type: ignore[assignment]
    """A list of all log messages. Shared between all Terminal.Logs widgets."""

    @property
    def namespace_bindings(self) -> NamespaceBindingsMapType:
        """Provides the ability to control the binding order in the footer"""
        return self.__sort_bindings(super().namespace_bindings)

    def on_mount(self) -> None:
        self.console.set_window_title("Clive")

        Communication.start()

        self.background_tasks = BackgroundTasks(exception_handler=self.__handle_background_error)
        self.background_tasks.run_every(timedelta(seconds=3), self.__update_data_from_node)
        if settings.LOG_DEBUG_LOOP:
            self.background_tasks.run_every(timedelta(seconds=1), self.__debug_log)

        self.push_screen(DashboardInactive())
        if (
            not (
                self.profile_data.name is not None
                and len(self.profile_data.name) > 0
                and self.profile_data.password is not None
                and len(self.profile_data.password) > 0
                and self.profile_data.node_address is not None
            )
            or settings.FORCE_ONBOARDING
        ):
            self.push_screen(Onboarding())

    async def on_unmount(self) -> None:
        await Communication.close()

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
        ScreenNotFoundError is raised if no screen was found.
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
        Because of textual's event ScreenResume not being bubbled up, we can't easily hook on it via
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

    def activate(self, active_mode_time: timedelta | None = None) -> None:
        def __auto_deactivate() -> None:
            self.deactivate()
            message = "Mode switched to [bold red]inactive[/] because the active mode time has expired."
            logger.info(message)
            Notification(message, category="info").show()

        command = Activate(
            self.app_state, self.background_tasks, active_mode_time=active_mode_time, auto_deactivate=__auto_deactivate
        )
        command.execute()
        if command.result:
            self.update_reactive("app_state")
            self.post_message_to_everyone(ActivateScreen.Succeeded())

    def deactivate(self) -> None:
        command = Deactivate(self.app_state, self.background_tasks)
        command.execute()
        if command.result:
            self.update_reactive("app_state")
            self.switch_screen("dashboard_inactive")

    def update_reactive(self, attribute_name: str, update_function: Callable[[Any], None] | None = None) -> None:
        """
        Reactive attributes of Textual are unable to detect changes to their own attributes
        (if we are dealing with a non-primitive type like a custom class).
        In order to notify watchers of a reactive attribute, it would have to be re-instantiated with the modified
        attributes. (See https://github.com/Textualize/textual/discussions/1099#discussioncomment-4047932)
        This is where this method comes in handy.
        """
        try:
            attribute = getattr(self, attribute_name)
        except AttributeError as error:
            raise AttributeError(f"{error}. Available ones are: {list(self._reactives)}") from error

        descriptor = self.__class__.__dict__[attribute_name]

        if update_function is not None:
            update_function(attribute)  # modify attributes of the reactive attribute

        # now we trigger the descriptor.__set__ method like the `self.attribute_name = value` would do
        if not descriptor._always_update:
            # that means, watchers won't be notified unless __ne__ returns False, we could bypass with `always_update`
            descriptor._always_update = True
            setattr(self, attribute_name, attribute)
            descriptor._always_update = False
        else:
            # we just need to trigger descriptor.__set__
            setattr(self, attribute_name, attribute)

    def post_message_to_everyone(self, message: Message) -> None:
        """Post a message to all screens in the stack."""
        for screen in reversed(self.screen_stack):
            screen.post_message(message)

    def post_message_to_screen(self, screen: str | type[Screen], message: Message) -> None:
        """
        Post a message to a specific screen in the stack.
        """
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
        self.update_reactive("profile_data")

    @staticmethod
    def __sort_bindings(data: NamespaceBindingsMapType) -> NamespaceBindingsMapType:
        """Sorts bindings by placing the ESC key at first place and fn keys at the end of the dictionary.
        This is done so that the bindings in the footer are displayed in a correct, uniform way.

        Args:
            data: The bindings to sort.
        Returns:
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

    def __update_data_from_node(self) -> None:
        logger.info("Updating mock data...")
        self.node_data.recalc()
        self.update_reactive("node_data")

    async def __debug_log(self) -> None:
        logger.debug("===================== DEBUG =====================")
        logger.debug(f"Currently focused: {self.focused}")
        logger.debug(f"Screen stack: {self.screen_stack}")
        logger.debug(f"Background tasks: { {name: task._state for name, task in self.background_tasks.tasks.items()} }")

        query = {"jsonrpc": "2.0", "method": "database_api.get_dynamic_global_properties", "id": 1}
        response = await Communication.arequest(str(self.profile_data.node_address), data=query)
        result = response.json()
        logger.debug(f'Current block: {result["result"]["head_block_number"]}')

        logger.debug("=================================================")


clive_app = Clive()

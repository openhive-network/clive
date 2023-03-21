from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Literal, overload

from textual.app import App
from textual.binding import Binding
from textual.reactive import reactive, var

from clive.config import settings
from clive.enums import AppMode
from clive.storage.mock_database import NodeData, ProfileData
from clive.ui.app_state import AppState
from clive.ui.background_tasks import BackgroundTasks
from clive.ui.dashboard.dashboard_active import DashboardActive
from clive.ui.dashboard.dashboard_inactive import DashboardInactive
from clive.ui.onboarding.onboarding import Onboarding
from clive.ui.quit.quit import Quit
from clive.ui.shared.help import Help
from clive.ui.terminal.command_line import CommandLinePrompt
from clive.ui.widgets.notification import Notification
from clive.version import VERSION_INFO

if TYPE_CHECKING:
    from datetime import timedelta

    from rich.console import RenderableType
    from textual.message import Message
    from textual.screen import Screen
    from textual.widget import AwaitMount


class Clive(App[int]):
    """A singleton instance of the Clive app."""

    SUB_TITLE = VERSION_INFO

    CSS_PATH = list(Path(__file__).parent.glob("**/*.scss"))

    BINDINGS = [
        Binding("ctrl+c", "push_screen('quit')", "Quit", show=False),
        Binding("ctrl+t", "terminal", "Toggle terminal", show=False),
        Binding("ctrl+s", "app.screenshot()", "Screenshot", show=False),
        Binding("?", "help", "Show help", show=False),
        Binding("l", "mock_log", "Mock log", show=False),
    ]

    SCREENS = {
        "quit": Quit,
        "dashboard_inactive": DashboardInactive,
        "dashboard_active": DashboardActive,
    }

    header_expanded = var(False)
    """Synchronize the expanded header state in all created header objects."""

    terminal_expanded = var(False)

    node_data = var(NodeData())

    profile_data = var(ProfileData.load())

    app_state = var(AppState())

    logs: reactive[list[RenderableType | object]] = reactive([], repaint=False, init=False, always_update=True)
    """A list of all log messages. Shared between all Terminal.Logs widgets."""

    def on_mount(self) -> None:
        self.console.set_window_title("Clive")
        self.background_tasks = BackgroundTasks(self)

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

    def push_screen(self, screen: Screen | str) -> AwaitMount:
        return self.__update_screen("push_screen", screen)

    def push_screen_at(self, index: int, screen: Screen | str) -> None:
        """Push a screen at the given index in the stack."""
        screen_, _ = self.app._get_screen(screen)
        self.app._screen_stack.insert(index, screen_)

    def pop_screen(self) -> Screen:
        return self.__update_screen("pop_screen")

    def pop_screen_until(self, screen: str | type[Screen]) -> None:
        """Pop all screens until the given screen is on top of the stack."""

        screen_name = screen if isinstance(screen, str) else screen.__name__
        self.__assert_screen_name_in_stack(screen_name)

        with self.batch_update():
            while self.screen_stack[-1].__class__.__name__ != screen_name:
                self.pop_screen()

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
        self.terminal_expanded = not self.terminal_expanded

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

    def activate(self, permanent_active: bool = False, active_mode_time: timedelta | None = None) -> None:
        def __update_function(app_state: AppState) -> None:
            app_state.mode = AppMode.ACTIVE
            app_state.permanent_active = permanent_active

        def __auto_deactivate() -> None:
            self.deactivate()
            message = "Mode switched to [bold red]inactive[/] because the active mode time has expired."
            self.log(message)
            Notification(message, category="info").show()

        if permanent_active and active_mode_time:
            raise ValueError("Can't set both permanent_active and active_mode_time.")

        if active_mode_time:
            self.background_tasks.run_after(active_mode_time, __auto_deactivate)

        self.update_reactive("app_state", __update_function)
        self.app.switch_screen("dashboard_active")

    def deactivate(self) -> None:
        def __update_function(app_state: AppState) -> None:
            app_state.mode = AppMode.INACTIVE

        # cancel pending "auto_deactivate" background task if any
        self.background_tasks.cancel("run_after___auto_deactivate")

        self.update_reactive("app_state", __update_function)
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
        screen_name = screen if isinstance(screen, str) else screen.__name__
        self.__assert_screen_name_in_stack(screen_name)

        for screen_ in reversed(self.screen_stack):
            if screen_.__class__.__name__ == screen_name:
                screen_.post_message(message)

    def __assert_screen_name_in_stack(self, screen_name: str) -> None:
        if screen_name not in [screen.__class__.__name__ for screen in self.screen_stack]:
            raise ValueError(f"Screen {screen_name} is not in the screen stack.\nScreen stack: {self.screen_stack}")


clive_app = Clive()

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Literal

from textual.app import App
from textual.binding import Binding
from textual.reactive import reactive, var

from clive.enums import AppMode
from clive.storage.mock_database import NodeAddress, NodeData, ProfileData
from clive.ui.app_state import AppState
from clive.ui.dashboard.dashboard_active import DashboardActive
from clive.ui.dashboard.dashboard_inactive import DashboardInactive
from clive.ui.login.login import Login
from clive.ui.quit.quit import Quit
from clive.ui.registration.registration import Registration
from clive.ui.terminal.terminal import CommandLinePrompt
from clive.version import VERSION_INFO

if TYPE_CHECKING:
    from rich.console import RenderableType


class Clive(App[int]):
    """A singleton instance of the Clive app."""

    SUB_TITLE = VERSION_INFO

    CSS_PATH = [
        Path(__file__).parent / "global.scss",
        Path(__file__).parent / "quit/quit.scss",
        Path(__file__).parent / "widgets/header.scss",
        Path(__file__).parent / "widgets/titled_label.scss",
        Path(__file__).parent / "login/login.scss",
        Path(__file__).parent / "registration/registration.scss",
        Path(__file__).parent / "dashboard/dashboard.scss",
        Path(__file__).parent / "terminal/terminal.scss",
    ]

    BINDINGS = [
        Binding("ctrl+c", "push_screen('quit')", "Quit"),
        Binding("ctrl+t", "terminal", "Toggle terminal"),
        Binding("l", "mock_log", "Mock log"),
    ]

    SCREENS = {
        "quit": Quit,
        "dashboard_inactive": DashboardInactive,
        "dashboard_active": DashboardActive,
        "login": Login,
        "registration": Registration,
    }

    header_expanded = var(False)
    """Synchronize the expanded header state in all created header objects."""

    terminal_expanded = var(False)

    node_data = var(NodeData())

    profile_data = var(ProfileData())

    app_state = var(AppState())

    logs: reactive[list[RenderableType | object]] = reactive([], repaint=False, init=False, always_update=True)
    """A list of all log messages. Shared between all Terminal.Logs widgets."""

    def on_mount(self) -> None:
        self.console.set_window_title("Clive")
        asyncio.create_task(self.background_task())
        asyncio.create_task(self.debug_task())
        self.push_screen("dashboard_inactive")

    def action_terminal(self) -> None:
        self.terminal_expanded = not self.terminal_expanded

    def action_mock_log(self) -> None:
        self.write("This is a mock log.", message_type="info")

    def write(self, text: RenderableType, *, message_type: Literal["info", "warning", "input"] | None = None) -> None:
        if message_type == "info":
            text = f"[blue]INFO:[/blue] {text}"
        elif message_type == "input":
            prefix = self.query(CommandLinePrompt).first(CommandLinePrompt).get_current_prompt()
            text = f"{prefix} {text}"

        self.logs += [text]

    async def background_task(self) -> None:
        def __update_function(profile_data: ProfileData) -> None:
            profile_data.node_address = NodeAddress("https", str(uuid.uuid4()))

        while True:
            await asyncio.sleep(3)
            self.log("Updating mock data...")
            self.update_reactive("profile_data", __update_function)

            self.node_data.recalc()
            self.update_reactive("node_data")

    async def debug_task(self) -> None:
        while True:
            await asyncio.sleep(1)
            self.log("===================== DEBUG =====================")
            self.log(f"Screen stack: {self.screen_stack}")
            self.log("=================================================")

    def activate(self) -> None:
        def __update_function(app_state: AppState) -> None:
            app_state.mode = AppMode.ACTIVE

        self.update_reactive("app_state", __update_function)

    def deactivate(self) -> None:
        def __update_function(app_state: AppState) -> None:
            app_state.mode = AppMode.INACTIVE

        self.update_reactive("app_state", __update_function)

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


clive_app = Clive()

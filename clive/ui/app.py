from __future__ import annotations

import asyncio
import uuid
from copy import deepcopy
from pathlib import Path

from textual.app import App
from textual.binding import Binding
from textual.reactive import reactive, var

from clive.enums import AppMode
from clive.storage.mock_database import NodeAddress, NodeData, ProfileData
from clive.ui.app_state import AppState
from clive.ui.dashboard.dashboard_active import DashboardActive
from clive.ui.dashboard.dashboard_inactive import DashboardInactive
from clive.ui.quit.quit import Quit
from clive.version import VERSION_INFO


class Clive(App[int]):
    """A singleton instance of the Clive app."""

    SUB_TITLE = VERSION_INFO

    CSS_PATH = [
        Path(__file__).parent / "quit/quit.scss",
        Path(__file__).parent / "widgets/header.scss",
        Path(__file__).parent / "widgets/titled_label.scss",
        Path(__file__).parent / "login/login.scss",
        Path(__file__).parent / "registration/registration.scss",
    ]

    BINDINGS = [
        Binding("ctrl+c", "push_screen('quit')", "Quit"),
    ]

    SCREENS = {
        "quit": Quit,
        "dashboard_inactive": DashboardInactive,
        "dashboard_active": DashboardActive,
    }

    header_expanded = var(False)
    """Synchronize the expanded header state in all created header objects."""

    node_data = var(NodeData())

    profile_data = var(ProfileData())

    app_state = reactive(AppState(), repaint=False, always_update=True)

    def on_mount(self) -> None:
        asyncio.create_task(self.background_task())
        asyncio.create_task(self.debug_task())
        self.push_screen("dashboard_inactive")

    async def background_task(self) -> None:
        while True:
            await asyncio.sleep(3)
            self.log("Updating mock node_address...")
            new_data = deepcopy(self.profile_data)
            new_data.node_address = NodeAddress("https", str(uuid.uuid4()))
            self.profile_data = new_data

    async def debug_task(self) -> None:
        while True:
            await asyncio.sleep(1)
            self.log("===================== DEBUG =====================")
            self.log(f"Screen stack: {self.screen_stack}")
            self.log("=================================================")

    def activate(self) -> None:
        self.app_state.mode = AppMode.ACTIVE
        self.app_state = self.app_state  # we need to trigger descriptor __set__ method

    def deactivate(self) -> None:
        self.app_state.mode = AppMode.INACTIVE
        self.app_state = self.app_state  # we need to trigger descriptor __set__ method


clive_app = Clive()

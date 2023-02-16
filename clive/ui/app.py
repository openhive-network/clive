from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

from textual.app import App
from textual.binding import Binding
from textual.reactive import var

from clive.storage.mock_database import NodeAddress, mock_db
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
    ]

    BINDINGS = [
        Binding("ctrl+c", "push_screen('quit')", "Quit"),
    ]

    SCREENS = {
        "quit": Quit,
        "dashboard_inactive": DashboardInactive,
    }

    header_expanded = var(False)
    """Synchronize the expanded header state in all created header objects."""

    def on_mount(self) -> None:
        asyncio.create_task(self.background_task())
        self.push_screen("dashboard_inactive")

    async def background_task(self) -> None:
        while True:
            await asyncio.sleep(3)
            self.log("Updating mock node_address...")
            mock_db.node_address = NodeAddress("https", str(uuid.uuid4()))


clive_app = Clive()

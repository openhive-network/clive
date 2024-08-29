from __future__ import annotations

from textual.binding import Binding

from clive.__private.ui.screens.dashboard import DashboardBase
from clive.__private.ui.screens.unlock import Unlock


class DashboardLocked(DashboardBase):
    BINDINGS = [
        Binding("f5", "unlock", "Unlock wallet"),
    ]

    def action_unlock(self) -> None:
        self.app.push_screen(Unlock())

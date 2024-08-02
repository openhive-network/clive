from __future__ import annotations

from textual.binding import Binding

from clive.__private.ui.dashboard.dashboard_base import DashboardBase
from clive.__private.ui.unlock.unlock import Unlock


class DashboardLocked(DashboardBase):
    BINDINGS = [
        Binding("f5", "unlock", "Unlock wallet"),
    ]

    def action_unlock(self) -> None:
        self.app.push_screen(Unlock())

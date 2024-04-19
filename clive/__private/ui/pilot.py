from __future__ import annotations

from typing import TYPE_CHECKING

from textual.pilot import Pilot

from clive_local_tools.tui.constants import TUI_TESTS_GENERAL_TIMEOUT

if TYPE_CHECKING:
    from clive.__private.ui.app import Clive


class ClivePilot(Pilot[int]):
    app: Clive

    async def _wait_for_screen(self, timeout: float = TUI_TESTS_GENERAL_TIMEOUT) -> bool:
        return await super()._wait_for_screen(timeout=timeout)

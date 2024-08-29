from __future__ import annotations

from typing import TYPE_CHECKING

from textual.pilot import Pilot

if TYPE_CHECKING:
    from clive.__private.ui.app import Clive


class ClivePilot(Pilot[int]):
    app: Clive

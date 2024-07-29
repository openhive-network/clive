from __future__ import annotations

from textual.widgets import Static


class NotImplementedYet(Static):
    def __init__(self) -> None:
        super().__init__(renderable="The functionality will be available soon.")

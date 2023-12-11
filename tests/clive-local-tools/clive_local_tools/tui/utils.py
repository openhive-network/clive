from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

if TYPE_CHECKING:
    from textual.app import App


def get_mode(app: App[int]) -> str:
    """Do not call while onboarding process."""
    widget = app.query_one("#mode-label").query_one("#value")
    return str(widget._DynamicLabel__label.renderable).strip(" ")  # type: ignore[attr-defined]


def current_view(app: App[int], nodes: bool = False) -> None:
    """For debug purposes."""
    tt.logger.debug(f"screen: {app.screen}, focused: {app.focused}")
    if nodes:
        tt.logger.debug(f'nodes: {app.query("*").nodes}')

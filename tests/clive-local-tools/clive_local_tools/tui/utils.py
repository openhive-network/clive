from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt
from textual.css.query import NoMatches

from clive.__private.ui.widgets.titled_label import TitledLabel

if TYPE_CHECKING:
    from clive_local_tools.tui.types import CliveApp


def log_current_view(app: CliveApp, *, nodes: bool = False, source: str | None = None) -> None:
    """For debug purposes."""
    source = f"{source}: " if source is not None else ""
    tt.logger.debug(f"{source}screen: {app.screen}, focused: {app.focused}")
    if nodes:
        tt.logger.debug(f'nodes: {app.screen.query("*").nodes}')


def get_profile_name(app: CliveApp) -> str:
    try:
        widget = app.screen.query_exactly_one("#profile-label", TitledLabel)
    except NoMatches as error:
        raise AssertionError("Profile couldn't be found. It is not available in the create_profile process.") from error
    return str(widget.value).strip()

from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt
from textual.css.query import NoMatches

from clive.__private.ui.widgets.titled_label import TitledLabel

if TYPE_CHECKING:
    from clive_local_tools.tui.types import CliveApp


def get_mode(app: CliveApp) -> str:
    """Do not call while onboarding process."""
    try:
        widget = app.query_one("#mode-label", TitledLabel)
    except NoMatches as error:
        raise AssertionError("Mode couldn't be found. It is not available in the onboarding process.") from error
    return str(widget.value).strip()


def log_current_view(app: CliveApp, *, nodes: bool = False) -> None:
    """For debug purposes."""
    tt.logger.debug(f"screen: {app.screen}, focused: {app.focused}")
    if nodes:
        tt.logger.debug(f'nodes: {app.query("*").nodes}')

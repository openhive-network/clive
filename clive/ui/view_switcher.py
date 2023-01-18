from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from clive.exceptions import ViewDoesNotExist
from clive.ui.view_manager import view_manager

if TYPE_CHECKING:
    from clive.ui.view import View


def switch_view(view: str | View) -> None:
    if isinstance(view, str):
        from clive.ui.views.views_holder import views

        try:
            view = views[view]
        except KeyError:
            raise ViewDoesNotExist(f"View '{view}' does not exist. Available views: {list(views)}")

    logger.info(f"Switching view to {view}")

    view_manager.active_view = view

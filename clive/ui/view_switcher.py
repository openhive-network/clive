from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from clive.app import clive
from clive.exceptions import ViewDoesNotExist
from clive.ui.root_component import root_component

if TYPE_CHECKING:
    from clive.ui.view import View


def switch_view(view: str | View) -> None:
    if isinstance(view, str):
        from clive.ui.views import views

        try:
            view = views[view]
        except KeyError:
            raise ViewDoesNotExist(f"View '{view}' does not exist. Available views: {list(views)}")

    logger.info(f"Switching view to {view}")

    container = view.component.container
    root_component.container = container
    clive.set_focus(container)

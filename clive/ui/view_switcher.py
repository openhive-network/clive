from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from clive.app import clive
from clive.ui.root_component import root_component

if TYPE_CHECKING:
    from clive.ui.view import View


def switch_view(view: str | View) -> None:
    if isinstance(view, str):
        from clive.ui.views import views

        view = views[view]

    logger.info(f"Switching view to {view}")

    container = view.component.container
    root_component.container = container
    clive.set_focus(container)

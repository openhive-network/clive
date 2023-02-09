from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.ui.view_manager import ViewManager


def get_view_manager() -> ViewManager:
    from clive.ui.view_manager import view_manager

    return view_manager

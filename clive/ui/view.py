from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Sequence

from clive.enums import AppMode
from clive.ui.component import Component
from clive.ui.get_view_manager import get_view_manager
from clive.ui.mode_restricted import ModeRestricted

if TYPE_CHECKING:
    from clive.ui.view_manager import ViewManager  # noqa: F401


class View(ModeRestricted, Component["ViewManager"], ABC):
    """
    A view is a kind of component that consists of other components and determines their final layout/arrangement.
    It should not be part of another view or component. Specifies the final appearance that can be shown to the user.
    """

    def __init__(self, *, available_in_modes: Sequence[AppMode] = (AppMode.ANY,)) -> None:
        super().__init__(parent=get_view_manager(), modes=available_in_modes)

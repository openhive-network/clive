from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from clive.ui.component import Component

if TYPE_CHECKING:
    from clive.ui.view_manager import ViewManager  # noqa: F401


class View(Component["ViewManager"], ABC):
    """
    A view is a kind of component that consists of other components and determines their final layout/arrangement.
    It should not be part of another view or component. Specifies the final appearance that can be shown to the user.
    """

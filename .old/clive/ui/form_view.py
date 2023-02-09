from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Callable, Dict, Sequence

from clive.enums import AppMode
from clive.ui.component import Component
from clive.ui.mode_restricted import ModeRestricted

if TYPE_CHECKING:
    from clive.ui.views.form import Form

RequestedButtonsT = Dict[str, Callable[[], None]]


class FormView(ModeRestricted, Component["Form"], ABC):
    """
    A view that is used to display in a multistep form.
    """

    def __init__(self, parent: Form, *, modes: Sequence[AppMode] = (AppMode.ANY,)) -> None:
        super().__init__(parent=parent, modes=modes)

    def requested_buttons(self) -> RequestedButtonsT:
        """
        Returns dictionaries of handles, that should be added to buttons
        by parent to user interface

        Returns:
            Dict[str, Callable[[],None]]: key is displayed label on button, and value
                                            is handler for Button
        """
        return {}

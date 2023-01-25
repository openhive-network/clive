from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Callable, Dict

from clive.ui.component import Component

if TYPE_CHECKING:
    from clive.ui.views.form import Form  # noqa: F401

RequestedButtonsT = Dict[str, Callable[[], None]]


class FormView(Component["Form"], ABC):
    """
    A view that is used to display in a multistep form.
    """

    def requested_buttons(self) -> RequestedButtonsT:
        """
        Returns dictionaries of handles, that should be added to buttons
        by parent to user interface

        Returns:
            Dict[str, Callable[[],None]]: key is displayed label on button, and value
                                            is handler for Button
        """
        return {}

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, ParamSpec

from textual.dom import DOMNode
from textual.screen import Screen

from clive.__private.core.commands.abc.command_in_active import CommandRequiresActiveModeError
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from collections.abc import Callable

P = ParamSpec("P")


class CliveScreen(Screen, CliveWidget):
    """
    An ordinary textual screen that also knows what type of application it belongs to.

    Inspired by: https://github.com/Textualize/textual/discussions/1099#discussioncomment-4049612
    """

    @staticmethod
    def try_again_after_activation(func: Callable[P, None]) -> Callable[P, None]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
            self = args[0]
            assert isinstance(self, DOMNode)

            try:
                func(*args, **kwargs)
            except CommandRequiresActiveModeError:
                from clive.__private.ui.activate.activate import Activate

                def _on_activation_result(value: bool) -> None:
                    if not value:
                        Notification("Aborted. Active mode is required for this action.", category="warning").show()
                        return

                    func(*args, **kwargs)

                self.app.push_screen(Activate(activation_result_callback=_on_activation_result))

        return wrapper

    def on_mount(self) -> None:
        if self.app.focused is None:
            self.focus_next()

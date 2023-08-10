from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, ParamSpec

from textual.screen import Screen, ScreenResultType

from clive.__private.core.commands.abc.command_in_active import CommandRequiresActiveModeError
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from clive.__private.ui.app import Clive


P = ParamSpec("P")


class CliveScreen(Screen[ScreenResultType], CliveWidget):
    """
    An ordinary textual screen that also knows what type of application it belongs to.

    Inspired by: https://github.com/Textualize/textual/discussions/1099#discussioncomment-4049612
    """

    @staticmethod
    def try_again_after_activation(
        *, app: Clive | None = None
    ) -> Callable[[Callable[P, Awaitable[None]]], Callable[P, Awaitable[None]]]:
        def decorator(func: Callable[P, Awaitable[None]]) -> Callable[P, Awaitable[None]]:
            @wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
                if not app:
                    self = args[0]
                    assert isinstance(self, CliveWidget), f"{type(self)} is not a CliveWidget"
                    app_ = self.app
                else:
                    app_ = app

                try:
                    await func(*args, **kwargs)
                except CommandRequiresActiveModeError:
                    from clive.__private.ui.activate.activate import Activate

                    async def _on_activation_result(value: bool) -> None:
                        if not value:
                            app_.notify("Aborted. Active mode is required for this action.", severity="warning")
                            return

                        await func(*args, **kwargs)

                    app_.push_screen(Activate(activation_result_callback=_on_activation_result))

            return wrapper

        return decorator

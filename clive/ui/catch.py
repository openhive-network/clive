from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Optional

from prompt_toolkit import HTML
from prompt_toolkit.formatted_text.base import AnyFormattedText
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import AnyContainer, Dimension, HorizontalAlign, HSplit, VerticalAlign, VSplit
from prompt_toolkit.widgets import Box, Button, Frame, Label

from clive.exceptions import FloatException
from clive.ui.containerable import Containerable
from clive.ui.focus import set_focus
from clive.ui.get_view_manager import get_view_manager


class ErrorFloat(Containerable):
    def __init__(self, message: AnyFormattedText) -> None:
        self.__message = message
        super().__init__()
        get_view_manager().error_float = self
        set_focus(self.container)

    def _create_container(self) -> AnyContainer:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.__ok)

        return Frame(
            HSplit(
                [
                    Box(
                        Label(self.__message, dont_extend_height=False, style="fg: #ff0000"),
                        Dimension(min=1, max=10),
                        padding_right=5,
                    ),
                    VSplit(
                        [Button("<F1> Ok", handler=self.__ok, left_symbol="", right_symbol="")],
                        align=HorizontalAlign.CENTER,
                        padding=Dimension(min=1),
                    ),
                ],
                align=VerticalAlign.CENTER,
            ),
            title=HTML("""<style fg="#ff0000"><b>~ ERROR ~</b></style>"""),
            key_bindings=kb,
        )

    def __ok(self, _: KeyPressEvent | None = None) -> None:
        get_view_manager().error_float = None


EventT = Callable[[Any, Optional[KeyPressEvent]], None]


def catch(foo: EventT) -> EventT:
    @wraps(foo)
    def catch_impl(*args: Any, **kwargs: Any) -> None:
        try:
            return foo(*args, **kwargs)
        except FloatException as ex:
            ErrorFloat(ex.info())

    return catch_impl

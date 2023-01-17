from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from loguru import logger
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.styles import Style

from clive.config import settings
from clive.ui.root_component import root_component

if TYPE_CHECKING:
    from prompt_toolkit.layout.layout import FocusableElement


class Clive:
    REFRESH_INTERVAL: Final[float] = 0.25

    def __init__(self) -> None:
        self.__app = self.__create_app()

    def run(self) -> None:
        from clive.ui.view_switcher import switch_view

        switch_view("welcome")
        self.__app.run()

    def set_focus(self, container: FocusableElement) -> None:
        logger.debug(f"Setting focus to: {container}")
        self.__app.layout.focus(container)

    def __create_app(self) -> Application[Any]:
        return Application(
            layout=Layout(root_component.container),
            style=Style.from_dict(settings.style),
            key_bindings=self.__get_key_bindings(),
            full_screen=True,
            mouse_support=True,
            refresh_interval=self.REFRESH_INTERVAL,
        )

    @staticmethod
    def __get_key_bindings() -> KeyBindings:
        kb = KeyBindings()

        kb.add(Keys.Tab)(focus_next)
        kb.add(Keys.BackTab)(focus_previous)

        @kb.add(Keys.ControlC)
        def _(event: KeyPressEvent) -> None:
            event.app.exit()

        return kb


clive = Clive()

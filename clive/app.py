from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Final, Literal

from loguru import logger
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.styles import Style

from clive.config import settings
from clive.ui.get_view_manager import get_view_manager
from clive.ui.menus.menu_empty import MenuEmpty

if TYPE_CHECKING:
    from prompt_toolkit.layout.layout import FocusableElement


class Clive:
    REFRESH_INTERVAL: Final[float] = 0.25

    def __init__(self) -> None:
        self.__app = self.__create_app()
        self.__skip_menu_on_focus = True

    def run(self) -> None:
        from clive.ui.view_switcher import switch_view

        switch_view("login")
        self.__app.run()

    def set_focus(self, container: FocusableElement) -> None:
        logger.debug(f"Setting focus to: {container}")
        self.__app.layout.focus(container)

    def __create_app(self) -> Application[Any]:
        return Application(
            layout=Layout(get_view_manager().active_container),
            style=Style.from_dict(settings.style),
            key_bindings=self.__get_key_bindings(),
            full_screen=True,
            mouse_support=True,
            refresh_interval=self.REFRESH_INTERVAL,
            after_render=lambda _: self.__set_focus_automatically(),
        )

    def __set_focus_automatically(self) -> None:
        self.__app.layout.focus(get_view_manager().active_container)

        # switch to first focusable element, skipping the first one (Menu)
        if self.__skip_menu_on_focus and not self.__is_menu_body_focused():
            self.__skip_menu_on_focus = False
            self.__app.layout.focus_next()

    def __is_menu_body_focused(self) -> bool:
        # The container property of MenuContainer class stores FloatContainer which contents is HSplit storing
        # window and body. What we want to check is if the body is focused, and window takes over the focus.
        return self.__app.layout.has_focus(get_view_manager().menu.container.container.content.children[1])  # type: ignore

    def __get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        kb.add(Keys.Tab)(self.__focus("next"))
        kb.add(Keys.BackTab)(self.__focus("previous"))

        @kb.add(Keys.ControlC)
        def _(event: KeyPressEvent) -> None:
            event.app.exit()

        return kb

    def __focus(self, direction: Literal["next", "previous"]) -> Callable[[KeyPressEvent], None]:
        def focus(event: KeyPressEvent) -> None:
            fun = self.__app.layout.focus_next if direction == "next" else self.__app.layout.focus_previous
            fun()

            if isinstance(get_view_manager().menu, MenuEmpty) and self.__is_menu_focused():  # skip focusing MenuEmpty
                fun()

        return focus

    def __is_menu_focused(self) -> bool:
        menu_window = get_view_manager().menu.container.window
        return self.__app.layout.has_focus(menu_window)

    def exit(self) -> None:
        self.__app.exit()

    def skip_menu_on_focus(self) -> None:
        self.__skip_menu_on_focus = True


clive = Clive()

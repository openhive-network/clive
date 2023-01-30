from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Final, Literal

from loguru import logger
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.styles import Style

from clive.config import settings
from clive.storage.mock_database import MockDB
from clive.ui.get_view_manager import get_view_manager
from clive.ui.input_field import input_field
from clive.ui.menus.menu_empty import MenuEmpty
from clive.ui.views.button_based import ButtonsBased

if TYPE_CHECKING:
    from prompt_toolkit.layout import Window
    from prompt_toolkit.layout.layout import FocusableElement


class Clive:
    REFRESH_INTERVAL: Final[float] = 3

    def __init__(self) -> None:
        self.__app = self.__create_app()

    def run(self) -> None:
        from clive.ui.view_switcher import switch_view

        switch_view("registration")
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
            on_invalidate=lambda _: MockDB.node.recalc(),
            min_redraw_interval=0.1,
        )

    def __get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        kb.add(Keys.Tab)(self.__focus("next"))
        kb.add(Keys.BackTab)(self.__focus("previous"))

        @kb.add(Keys.ControlC)
        def _(event: KeyPressEvent) -> None:
            event.app.exit()

        @kb.add(self.__get_bind_from_config("focus_menu"))
        def _(event: KeyPressEvent) -> None:
            if not isinstance(get_view_manager().menu, MenuEmpty):
                self.set_focus(self.__get_menu_window())

        @kb.add(self.__get_bind_from_config("focus_buttons"))
        def _(event: KeyPressEvent) -> None:
            if isinstance(get_view_manager().active_view, ButtonsBased):
                view: ButtonsBased = get_view_manager().active_view  # type: ignore
                self.set_focus(view.buttons.container)

        @kb.add(self.__get_bind_from_config("focus_input_field"))
        def _(event: KeyPressEvent) -> None:
            if isinstance(get_view_manager().active_view, ButtonsBased):
                self.set_focus(input_field.container)

        @kb.add(Keys.ControlSpace)
        def _(event: KeyPressEvent) -> None:
            """Start auto completion. If the menu is showing already, select the next completion."""
            current_buffer = event.app.current_buffer
            if current_buffer.complete_state:
                current_buffer.complete_next()
            else:
                current_buffer.start_completion(select_first=False)

        return kb

    def __focus(self, direction: Literal["next", "previous"]) -> Callable[[KeyPressEvent], None]:
        def focus(event: KeyPressEvent) -> None:
            fun = self.__app.layout.focus_next if direction == "next" else self.__app.layout.focus_previous
            fun()

            if isinstance(get_view_manager().menu, MenuEmpty) and self.__is_menu_focused():  # skip focusing MenuEmpty
                fun()

        return focus

    def __is_menu_focused(self) -> bool:
        # The container property of MenuContainer class stores FloatContainer which content is HSplit storing
        # window and body. When we want to check if menu body is focused just by menu.container - window
        # takes over the focus.
        return self.__app.layout.has_focus(self.__get_menu_window())

    @staticmethod
    def __get_menu_window() -> Window:
        return get_view_manager().menu.container.window

    @staticmethod
    def __get_bind_from_config(name: str) -> Keys:
        binding = settings.key_bindings[name]
        try:
            return Keys(binding)
        except ValueError as e:
            raise ValueError(f"Invalid key binding: {binding}.") from e

    def exit(self) -> None:
        self.__app.exit()


clive = Clive()

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from clive.ui.form_view import FormView
from clive.ui.get_view_manager import get_view_manager

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer

    from clive.ui.components.buttons_menu import ButtonsMenu, T
    from clive.ui.containerable import Containerable
    from clive.ui.form_view import RequestedButtonsT
    from clive.ui.views.form import Form


class QuickFormView(FormView):
    def __init__(self, *, parent: Form, body: Containerable, buttons: Optional[ButtonsMenu[T]] = None):
        self.__body = body
        self._set_buttons(buttons)
        super().__init__(parent)

    def _set_buttons(self, buttons: Optional[ButtonsMenu[T]]) -> None:
        def create_handler(handler: Optional[Callable[[], None]]) -> Callable[[], None]:
            def handler_impl() -> None:
                current_float = get_view_manager().float
                float_exist_before_call = current_float is not None

                if handler is not None:
                    handler()

                    current_float = get_view_manager().float
                    if not float_exist_before_call and (current_float is not None):
                        current_float.close_callback = self._parent._update_main_panel
                    else:
                        self._parent._update_main_panel()

            return handler_impl

        self.__requested_buttons = (
            {bt.text: create_handler(bt.handler) for bt in buttons._create_buttons()} if buttons is not None else {}
        )

    def requested_buttons(self) -> RequestedButtonsT:
        return self.__requested_buttons

    def _create_container(self) -> AnyContainer:
        return self.__body._create_container()

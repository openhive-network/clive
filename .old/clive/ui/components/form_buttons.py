from __future__ import annotations

import re
from typing import TYPE_CHECKING, Callable, List

from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.ui.catch import catch
from clive.ui.components.buttons_menu import ButtonsMenu

if TYPE_CHECKING:
    from clive.ui.form_view import FormView
    from clive.ui.views.form import Form

STANDARD_FUNCTIONAL_KEYS: List[Keys] = [getattr(Keys, f"F{i}") for i in range(1, 13)]


class FormButtons(ButtonsMenu["Form"]):
    def _create_buttons(self) -> List[Button]:
        return [
            Button("F1 Previous", handler=self.__f1_action),
            Button("F2 Next", handler=self.__f2_action),
            Button("F3 Cancel", handler=self.__f3_action),
            Button("F4 Finish", handler=self.__f4_action),
        ]

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.__f1_action)
        kb.add(Keys.F2)(self.__f2_action)
        kb.add(Keys.F3)(self.__f3_action)
        kb.add(Keys.F4)(self.__f4_action)

        return kb

    def __f1_action(self, _: KeyPressEvent | None = None) -> None:
        self._parent.previous_view()

    def __f2_action(self, _: KeyPressEvent | None = None) -> None:
        self._parent.next_view()

    def __f3_action(self, _: KeyPressEvent | None = None) -> None:
        self._parent.cancel()

    @catch
    def __f4_action(self, _: KeyPressEvent | None = None) -> None:
        self._parent.finish()

    @staticmethod
    def merge_buttons_and_actions(form: Form, form_view: FormView) -> FormButtons:
        return _FormButtonsMerged(form, form_view)


class _FormButtonsMerged(FormButtons):
    def __init__(self, form: Form, form_view: FormView) -> None:
        self.__form_view = form_view
        self.__additional_buttons = form_view.requested_buttons()
        self.__allowed_keys = STANDARD_FUNCTIONAL_KEYS.copy()

        for kb in super()._get_key_bindings().bindings:
            for key in kb.keys:
                assert isinstance(key, Keys)
                self.__allowed_keys.remove(key)

        super().__init__(form)

    def _create_buttons(self) -> List[Button]:
        buttons = super()._create_buttons()
        button_caption_regex = re.compile(r"^(F\d\d? )?(.*)")
        for i, kv in enumerate(self.__additional_buttons.items()):
            button_caption = kv[0]
            if (button_caption_match := button_caption_regex.match(button_caption)) is not None:
                button_caption = button_caption_match.group(2)
            buttons.append(
                Button(
                    text=f"{self.__allowed_keys[i].capitalize()} {button_caption}",
                    handler=self.__create_button_handler(kv[1]),
                )
            )
        return buttons

    def _get_key_bindings(self) -> KeyBindings:
        bindings = super()._get_key_bindings()
        for i, kv in enumerate(self.__form_view.requested_buttons().items()):
            bindings.add(self.__allowed_keys[i])(self.__create_button_handler(kv[1]))  # type: ignore
        return bindings

    def __create_button_handler(self, handler: Callable[[], None]) -> Callable[[], None]:
        def handler_impl(_: KeyPressEvent | None = None) -> None:
            handler()

        return handler_impl

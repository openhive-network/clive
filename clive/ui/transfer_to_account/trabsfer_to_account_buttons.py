from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.ui.components.buttons_menu import ButtonsMenu

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyPressEvent

    from clive.ui.transfer_to_account.transfer_to_account_view import TransferToAccountView


class TransferToAccountButtons(ButtonsMenu["TransferToAccountView"]):
    def __init__(self, parent: TransferToAccountView) -> None:
        super().__init__(parent)

    def _create_buttons(self) -> list[Button]:
        return [
            Button("F1 Transfer", handler=self.__f1_action),
            Button("F2 Save", handler=self.__f2_action),
            Button("F3 Cancel", handler=self.__f3_action),
        ]

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.__f1_action)
        kb.add(Keys.F2)(self.__f2_action)
        kb.add(Keys.F3)(self.__f3_action)
        return kb

    @staticmethod
    def __f1_action(_: KeyPressEvent | None = None) -> None:
        pass

    @staticmethod
    def __f2_action(_: KeyPressEvent | None = None) -> None:
        pass

    @staticmethod
    def __f3_action(_: KeyPressEvent | None = None) -> None:
        pass

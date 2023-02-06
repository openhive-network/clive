from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.view_switcher import switch_view
from clive.ui.widgets.button import Button

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyPressEvent

    from clive.ui.transfer_to_account.transfer_to_account_view import TransferToAccountView


class TransferToAccountButtons(ButtonsMenu["TransferToAccountView"]):
    def __init__(self, parent: TransferToAccountView) -> None:
        super().__init__(parent)

    def _create_buttons(self) -> list[Button]:  # type: ignore
        return [
            Button("F1 Process", handler=self.__f1_action),
            Button("F2 Cancel", handler=self.__f2_action),
        ]

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.__f1_action)
        kb.add(Keys.F2)(self.__f2_action)
        return kb

    @staticmethod
    def __f1_action(_: KeyPressEvent | None = None) -> None:
        logger.info("Should process to the summary view")

    @staticmethod
    def __f2_action(_: KeyPressEvent | None = None) -> None:
        switch_view("dashboard")

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

    from clive.ui.operation_summary.operation_summary_view import OperationSummaryView


class OperationSummaryButtons(ButtonsMenu["OperationSummaryView"]):
    def __init__(self, parent: OperationSummaryView) -> None:
        super().__init__(parent)

    def _create_buttons(self) -> list[Button]:  # type: ignore
        return [
            Button("F1 Send", handler=self.__f1_action),
            Button("F2 Preview", handler=self.__f2_action),
            Button("F3 Save", handler=self.__f3_action),
            Button("F4 Cancel", handler=self.__f4_action),
        ]

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.__f1_action)
        kb.add(Keys.F2)(self.__f2_action)
        kb.add(Keys.F3)(self.__f3_action)
        kb.add(Keys.F4)(self.__f4_action)
        return kb

    @staticmethod
    def __f1_action(_: KeyPressEvent | None = None) -> None:
        logger.info("Should send the operation")

    @staticmethod
    def __f2_action(_: KeyPressEvent | None = None) -> None:
        logger.info("Should preview the operation")

    @staticmethod
    def __f3_action(_: KeyPressEvent | None = None) -> None:
        logger.info("Should save the operation")

    @staticmethod
    def __f4_action(_: KeyPressEvent | None = None) -> None:
        switch_view("dashboard")

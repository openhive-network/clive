from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

from clive.app_status import app_status
from clive.exceptions import FormNotFinishedError
from clive.models.transfer_operation import TransferOperation
from clive.ui.catch import catch
from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.operation_summary.operation_summary_view import OperationSummaryView
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

    @catch
    def __f1_action(self, _: KeyPressEvent | None = None) -> None:
        checks = {
            "is to given": bool(self._parent.main_panel.to),
            "is amount given": bool(self._parent.main_panel.amount),
            "is memo given": bool(self._parent.main_panel.memo),
        }
        if not all(checks.values()):
            raise FormNotFinishedError(**checks)

        operation = TransferOperation(
            asset=self._parent.asset,
            from_=app_status.current_profile,
            to=self._parent.main_panel.to,
            amount=self._parent.main_panel.amount,
            memo=self._parent.main_panel.memo,
        )
        switch_view(OperationSummaryView(operation=operation, previous=self._parent))

    @staticmethod
    def __f2_action(_: KeyPressEvent | None = None) -> None:
        switch_view("dashboard")

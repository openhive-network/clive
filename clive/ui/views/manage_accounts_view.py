from __future__ import annotations

from typing import Sequence

from prompt_toolkit.widgets import Button
from prompt_toolkit.key_binding import KeyBindings

from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.components.radiolist_with_model import RadioListWithModel
from clive.ui.floats.create_account_float import CreateAccountFloat
from clive.ui.form_view import FormView
from clive.ui.form_view_convertible import FormViewConvertible
from clive.ui.quick_form_view import QuickFormView
from clive.ui.views.button_based import ButtonsBased
from clive.ui.views.form import Form
from clive.storage.mock_database import Account, MockDB

class ManageAccountsButtons(ButtonsMenu["ManageAccountsView"]):
    def __init__(self, parent: ManageAccountsView) -> None:
        super().__init__(parent)

    def _create_buttons(self) -> Sequence[Button]:
        return [
            Button("Create account", handler=self.__create_account),
            Button("Delete account", handler=self.__delete_account)
        ]

    def _get_key_bindings(self) -> KeyBindings:
        return KeyBindings()

    def __delete_account(self) -> None:
        MockDB.ACCOUNTS.remove(self._parent.main_panel.current_item[0])

    def __create_account(self) -> None:
        def on_account_object_created(account: Account):
            MockDB.ACCOUNTS.append(account)
            self._parent.main_panel._rebuild()
        CreateAccountFloat(on_account_object_created)

class ManageAccountsView(FormViewConvertible, ButtonsBased[RadioListWithModel["ManageAccountsView"], ManageAccountsButtons]):
    def __init__(self) -> None:
        super().__init__(RadioListWithModel(self, lambda: [(acc, acc.name) for acc in MockDB.ACCOUNTS]), ManageAccountsButtons(self))

    @staticmethod
    def convert_to_form_view(parent: Form) -> FormView:
        return QuickFormView(parent=parent, view=ManageAccountsView(), request_buttons={})

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, TypeVar, Union

from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.storage.mock_database import Account, MockDB
from clive.ui.component import T
from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.components.radiolist_with_model import RadioListWithModel
from clive.ui.form_view_convertible import FormViewConvertible
from clive.ui.manage_watched_accounts.add_new_watched_account_float import CreateWatchedAccountFloat
from clive.ui.quick_form_view import QuickFormView
from clive.ui.views.button_based import ButtonsBased
from clive.ui.views.form import Form

if TYPE_CHECKING:
    from clive.ui.form_view import FormView


ViewFormT = Union["ManageWatchedAccountView", Form]
K = TypeVar("K", bound="ManageWatchedAccountView | Form")


class ManageWatchedAccountsButtons(ButtonsMenu[K]):
    def __init__(self, parent: K, radio_list: RadioListWithModel[Account, K]) -> None:
        self.__radio_list: RadioListWithModel[Account, K] = radio_list
        super().__init__(parent=parent)

    def _create_buttons(self) -> List[Button]:
        return [
            Button("F1 CREATE", handler=self.__create_watched_account),
            Button("F2 DELETE", handler=self.__delete_watched_account),
        ]

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.__create_watched_account)
        kb.add(Keys.F2)(self.__delete_watched_account)
        return kb

    def __refresh_view_after_db_update(self, _: KeyPressEvent | None = None) -> None:
        self.__radio_list._rebuild()

    def __delete_watched_account(self, _: KeyPressEvent | None = None) -> None:
        if (item := self.__radio_list.current_item) is not None:
            MockDB.ACCOUNTS.remove(item)
        self.__refresh_view_after_db_update()

    def __create_watched_account(self, _: KeyPressEvent | None = None) -> None:
        def on_account_object_created(account: Account) -> None:
            MockDB.ACCOUNTS.append(account)
            self.__refresh_view_after_db_update()

        CreateWatchedAccountFloat(on_account_object_created)


class ManageWatchedAccountView(
    FormViewConvertible,
    ButtonsBased[
        RadioListWithModel[Account, "ManageWatchedAccountView"],
        ManageWatchedAccountsButtons["ManageWatchedAccountView"],
    ],
):
    def __init__(self) -> None:
        self.__radio_list: RadioListWithModel[
            Account, ManageWatchedAccountView
        ] = ManageWatchedAccountView.__create_radio_list(self)
        super().__init__(self.__radio_list, ManageWatchedAccountsButtons(self, self.__radio_list))

    @staticmethod
    def __create_radio_list(parent: T) -> RadioListWithModel[Account, T]:
        return RadioListWithModel(parent, get_model=lambda: [(acc, acc.name) for acc in MockDB.ACCOUNTS])

    @staticmethod
    def convert_to_form_view(parent: Form) -> FormView:
        obj = ManageWatchedAccountView.__create_radio_list(parent)

        def validator() -> Dict[str, bool]:
            return {"contains at least one account": (obj.current_item is not None)}

        quick_form_view = QuickFormView(parent=parent, body=obj, validator=validator)
        quick_form_view._set_buttons(ManageWatchedAccountsButtons(quick_form_view, obj))
        return quick_form_view

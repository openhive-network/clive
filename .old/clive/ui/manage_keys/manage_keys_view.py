from __future__ import annotations

from typing import TYPE_CHECKING, List, TypeVar, Union

from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.storage.mock_database import MockDB, PrivateKey
from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.components.radiolist_with_model import RadioListWithModel
from clive.ui.form_view_convertible import FormViewConvertible
from clive.ui.manage_keys.add_new_key_float import CreatePrivateKeyFloat
from clive.ui.quick_form_view import QuickFormView
from clive.ui.views.button_based import ButtonsBased

if TYPE_CHECKING:
    from clive.ui.component import T
    from clive.ui.form_view import FormView
    from clive.ui.views.form import Form


ViewFormT = Union["ManageKeysView", "Form"]
K = TypeVar("K", bound="ManageKeysView | Form")


class ManageKeysButtons(ButtonsMenu[K]):
    def __init__(self, parent: K, radio_list: RadioListWithModel[PrivateKey, K]) -> None:
        self.__radio_list: RadioListWithModel[PrivateKey, K] = radio_list
        super().__init__(parent=parent)

    def _create_buttons(self) -> List[Button]:
        return [
            Button("F1 CREATE", handler=self.__create_private_key),
            Button("F2 DELETE", handler=self.__delete_private_key),
        ]

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.__create_private_key)
        kb.add(Keys.F2)(self.__delete_private_key)
        return kb

    def __refresh_view_after_db_update(self) -> None:
        self.__radio_list._rebuild()

    def __delete_private_key(self, _: KeyPressEvent | None = None) -> None:
        MockDB.MAIN_ACTIVE_ACCOUNT.keys.remove(self.__radio_list.current_item)
        self.__refresh_view_after_db_update()

    def __create_private_key(self, _: KeyPressEvent | None = None) -> None:
        def on_account_object_created(pv_key: PrivateKey) -> None:
            MockDB.MAIN_ACTIVE_ACCOUNT.keys.append(pv_key)
            self.__refresh_view_after_db_update()

        CreatePrivateKeyFloat(on_account_object_created)


class ManageKeysView(
    FormViewConvertible,
    ButtonsBased[RadioListWithModel[PrivateKey, "ManageKeysView"], ManageKeysButtons["ManageKeysView"]],
):
    def __init__(self) -> None:
        self.__radio_list: RadioListWithModel[PrivateKey, ManageKeysView] = ManageKeysView.__create_radio_list(self)
        super().__init__(self.__radio_list, ManageKeysButtons(self, self.__radio_list))

    @staticmethod
    def __create_radio_list(parent: T) -> RadioListWithModel[PrivateKey, T]:
        return RadioListWithModel(
            parent,
            get_model=lambda: [(key, f"{key.key_name} [key={key.key}]") for key in MockDB.MAIN_ACTIVE_ACCOUNT.keys],
        )

    @staticmethod
    def convert_to_form_view(parent: Form) -> FormView:
        obj = ManageKeysView.__create_radio_list(parent)
        quick_form_view = QuickFormView(parent=parent, body=obj)
        quick_form_view._set_buttons(ManageKeysButtons(quick_form_view, obj))
        return quick_form_view

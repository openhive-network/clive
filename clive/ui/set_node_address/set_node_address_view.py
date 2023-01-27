from __future__ import annotations

from typing import TYPE_CHECKING, List, TypeVar, Union

from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.storage.mock_database import MockDB, NodeAddress
from clive.ui.component import T
from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.components.radiolist_with_model import RadioListWithModel
from clive.ui.form_view_convertible import FormViewConvertible
from clive.ui.quick_form_view import QuickFormView
from clive.ui.set_node_address.add_new_node_float import CreateNodeFloat
from clive.ui.views.button_based import ButtonsBased
from clive.ui.views.form import Form

if TYPE_CHECKING:
    from clive.ui.form_view import FormView

ViewFormT = Union["SetNodeAddressView", Form]
K = TypeVar("K", bound="SetNodeAddressView | Form")


class SetNodeAddressViewButtons(ButtonsMenu[K]):
    def __init__(self, parent: K, radio_list: RadioListWithModel[NodeAddress, K]) -> None:
        self.__radio_list: RadioListWithModel[NodeAddress, K] = radio_list
        super().__init__(parent=parent)

    def _create_buttons(self) -> List[Button]:
        return [
            Button("F1 CREATE", handler=self.__create_node),
            Button("F2 DELETE", handler=self.__delete_node),
            Button("F3 DEFAULT", handler=self.__set_as_default_node),
        ]

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.__create_node)
        kb.add(Keys.F2)(self.__delete_node)
        kb.add(Keys.F3)(self.__set_as_default_node)
        return kb

    def __refresh_view_after_db_update(self) -> None:
        self.__radio_list._rebuild()

    def __delete_node(self, _: KeyPressEvent | None = None) -> None:
        item_to_delete = self.__radio_list.current_item
        if item_to_delete == MockDB.NODE_ADDRESS:
            if len(MockDB.BACKUP_NODE_ADDRESSES) > 0:
                MockDB.NODE_ADDRESS = MockDB.BACKUP_NODE_ADDRESSES.pop(0)
            else:
                MockDB.NODE_ADDRESS = None
        else:
            MockDB.BACKUP_NODE_ADDRESSES.remove(item_to_delete)

        self.__refresh_view_after_db_update()

    def __create_node(self, _: KeyPressEvent | None = None) -> None:
        def on_node_created(node: NodeAddress) -> None:
            if MockDB.NODE_ADDRESS is None:
                MockDB.NODE_ADDRESS = node
            else:
                MockDB.BACKUP_NODE_ADDRESSES.append(node)
            self.__refresh_view_after_db_update()

        CreateNodeFloat(on_node_created)

    def __set_as_default_node(self, _: KeyPressEvent | None = None) -> None:
        future_default = self.__radio_list.current_item
        if future_default != MockDB.NODE_ADDRESS:
            assert MockDB.NODE_ADDRESS is not None
            MockDB.BACKUP_NODE_ADDRESSES.append(MockDB.NODE_ADDRESS)
            MockDB.NODE_ADDRESS = MockDB.BACKUP_NODE_ADDRESSES.pop(MockDB.BACKUP_NODE_ADDRESSES.index(future_default))
        self.__refresh_view_after_db_update()


class SetNodeAddressView(
    FormViewConvertible,
    ButtonsBased[
        RadioListWithModel[NodeAddress, "SetNodeAddressView"],
        SetNodeAddressViewButtons["SetNodeAddressView"],
    ],
):
    def __init__(self) -> None:
        self.__radio_list: RadioListWithModel[NodeAddress, SetNodeAddressView] = SetNodeAddressView.__create_radio_list(
            self
        )
        super().__init__(self.__radio_list, SetNodeAddressViewButtons(self, self.__radio_list))

    @staticmethod
    def __create_radio_list(parent: T) -> RadioListWithModel[NodeAddress, T]:
        return RadioListWithModel(
            parent,
            get_model=lambda: [
                (node, (("[*] " if node == MockDB.NODE_ADDRESS else "") + str(node)))
                for node in [
                    *([MockDB.NODE_ADDRESS] if MockDB.NODE_ADDRESS is not None else []),
                    *MockDB.BACKUP_NODE_ADDRESSES,
                ]
            ],
        )

    @staticmethod
    def convert_to_form_view(parent: Form) -> FormView:
        obj = SetNodeAddressView.__create_radio_list(parent)
        quick_form_view = QuickFormView(parent=parent, body=obj)
        quick_form_view._set_buttons(SetNodeAddressViewButtons(quick_form_view, obj))
        return quick_form_view

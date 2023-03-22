from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Label, Static

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.clive_widget import CliveWidget
from clive.ui.widgets.select.safe_select import SafeSelect
from clive.ui.widgets.select.select_item import SelectItem
from clive.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from textual.app import ComposeResult


class StaticPart(Static):
    """Static part of the screen"""


class ScrollablePart(Container, can_focus=True):
    """Scrollable part of the screen"""


class ActionsContainer(Horizontal):
    """Container for the all the actions - combobox"""


class ActionsSpacer(Static):
    """Spacer for the actions container"""


class KeyHint(Label):
    """Hint for the authority"""


class TransactionHint(Label):
    """Hint about the transaction"""


class OperationItem(Static):
    """Item in the operations list"""


class SelectKey(SafeSelect, CliveWidget):
    """Combobox for selecting the authority key"""

    def __init__(self) -> None:
        super().__init__(
            [SelectItem(x, x.key_name) for x in self.app.profile_data.working_account.keys],
            list_mount="ViewBag",
            selected=0,
            empty_string="no private key found",
        )


class TransactionSummary(BaseScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f1", "dashboard", "Dashboard"),
        Binding("f2", "save", "Save"),
        Binding("f10", "broadcast", "Broadcast"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__scrollable_part = ScrollablePart()
        self.__select_key = SelectKey()

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            with StaticPart():
                yield BigTitle("transaction summary")
                with ActionsContainer():
                    yield KeyHint("Sign with key:")
                    yield self.__select_key

                yield TransactionHint("This transaction will contain following operations in the presented order:")
            with self.__scrollable_part:
                for idx, operation in enumerate(self.app.profile_data.operations_cart):
                    yield OperationItem(operation.as_json(), classes="-even" if idx % 2 == 0 else "")
            yield Static()

    def action_dashboard(self) -> None:
        self.app.pop_screen_until("DashboardActive")

    def action_broadcast(self) -> None:
        self.__clear_all()
        self.action_dashboard()

    def action_save(self) -> None:
        with Path("transaction.json").open("w") as file:
            json.dump(
                self.__get_transaction_file_format(),
                file,
                default=vars,
            )

    def __clear_all(self) -> None:
        self.app.profile_data.operations_cart.clear()
        self.__scrollable_part.add_class("-hidden")

    def __get_transaction_file_format(self) -> dict[str, Any]:
        selected_authority = str(self.__select_key.selected.value) if self.__select_key.selected is not None else ""
        return {"ops_in_trx": self.app.profile_data.operations_cart, "selected_authority": selected_authority}

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Label, Static

from clive.__private.storage.mock_database import PrivateKey
from clive.__private.ui.activate.activate import Activate
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.select.safe_select import SafeSelect
from clive.__private.ui.widgets.select.select_item import SelectItem
from clive.__private.ui.widgets.select_file import SelectFile
from clive.__private.ui.widgets.view_bag import ViewBag

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


class SelectKey(SafeSelect[PrivateKey], CliveWidget):
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
        Binding("f2", "save", "Save"),
        Binding("f3", "dashboard", "Dashboard"),
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

    def on_activate_succeeded(self) -> None:
        self.__broadcast()

    def on_select_file_saved(self, event: SelectFile.Saved) -> None:
        file_path = event.file_path
        with Path(file_path).open("w") as file:
            json.dump(
                self.__get_transaction_file_format(),
                file,
                default=vars,
            )
        Notification(f"Transaction saved to [bold blue]'{file_path}'[/]", category="success").show()

    def action_dashboard(self) -> None:
        from clive.__private.ui.dashboard.dashboard_base import DashboardBase

        self.app.pop_screen_until(DashboardBase)

    def action_broadcast(self) -> None:
        if not self.app.app_state.is_active():
            self.app.push_screen(Activate())
            return

        self.__broadcast()

    def __broadcast(self) -> None:
        self.__clear_all()
        self.action_dashboard()
        Notification("Transaction broadcast successfully!", category="success").show()

    def action_save(self) -> None:
        self.app.push_screen(SelectFile(file_must_exist=False))

    def __clear_all(self) -> None:
        self.app.profile_data.operations_cart.clear()
        self.__scrollable_part.add_class("-hidden")

    def __get_transaction_file_format(self) -> dict[str, Any]:
        selected_authority = str(self.__select_key.selected.value)
        return {"ops_in_trx": self.app.profile_data.operations_cart, "selected_authority": selected_authority}

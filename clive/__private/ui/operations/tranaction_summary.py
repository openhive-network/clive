from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import Label, Static

from clive.__private.core.keys import PublicKey
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.ui.activate.activate import Activate
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.select.safe_select import SafeSelect
from clive.__private.ui.widgets.select_file import SelectFile
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.exceptions import CliveError, NoItemSelectedError

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Transaction


class TransactionCouldNotBeSignedError(CliveError):
    def __init__(self, transaction: Transaction, reason: str = "") -> None:
        self.transaction = transaction
        super().__init__(f"Transaction could not be signed: {transaction}, reason: {reason}")


class StaticPart(Static):
    """Static part of the screen."""


class ScrollablePart(ScrollableContainer, can_focus=True):
    """Scrollable part of the screen."""


class ActionsContainer(Horizontal):
    """Container for the all the actions - combobox."""


class ActionsSpacer(Static):
    """Spacer for the actions container."""


class KeyHint(Label):
    """Hint for the authority."""


class TransactionHint(Label):
    """Hint about the transaction."""


class OperationItem(Static):
    """Item in the operations list."""


class SelectKey(SafeSelect[PublicKey], CliveWidget):
    """Combobox for selecting the authority key."""

    def __init__(self) -> None:
        try:
            first_value = self.app.world.profile_data.working_account.keys.first
        except KeyNotFoundError:
            first_value = None

        super().__init__(
            [(key.alias, key) for key in self.app.world.profile_data.working_account.keys],
            value=first_value,
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
                for idx, operation in enumerate(self.app.world.profile_data.cart):
                    yield OperationItem(operation.json(by_alias=True), classes="-even" if idx % 2 == 0 else "")
            yield Static()

    @on(Activate.Succeeded)
    def activate_succeeded(self) -> None:
        self.__broadcast()

    @on(SelectFile.Saved)
    def save_to_file(self, event: SelectFile.Saved) -> None:
        file_path = event.file_path

        signed = None
        try:
            signed = self.__sign_transaction()
        except TransactionCouldNotBeSignedError as error:
            self.app.world.commands.save_to_file(transaction=error.transaction, path=file_path)
        else:
            self.app.world.commands.save_to_file(transaction=signed, path=file_path)

        self.notify(f"Transaction saved to [bold blue]'{file_path}'[/] {'(signed)' if signed else ''}")

    def action_dashboard(self) -> None:
        from clive.__private.ui.dashboard.dashboard_base import DashboardBase

        self.app.pop_screen_until(DashboardBase)

    def action_broadcast(self) -> None:
        if not self.app.world.app_state.is_active():
            self.app.push_screen(Activate())
            return

        self.__broadcast()

    def __broadcast(self) -> None:
        try:
            signed = self.__sign_transaction()
        except TransactionCouldNotBeSignedError as error:
            self.notify(str(error), severity="error")
            return

        if not self.app.world.commands.broadcast(transaction=signed).success:
            return

        self.__clear_all()
        self.action_dashboard()
        self.notify("Transaction broadcast successfully!")

    def action_save(self) -> None:
        self.app.push_screen(SelectFile(file_must_exist=False))

    def __clear_all(self) -> None:
        self.app.world.profile_data.cart.clear()
        self.__scrollable_part.add_class("-hidden")

    def __sign_transaction(self) -> Transaction:
        transaction = self.__build_transaction()

        try:
            value = self.__select_key.value
        except NoItemSelectedError as error:
            raise TransactionCouldNotBeSignedError(transaction, "No key was selected!") from error
        else:
            return self.app.world.commands.sign(transaction=transaction, sign_with=value).result_or_raise

    def __build_transaction(self) -> Transaction:
        return self.app.world.commands.build_transaction(operations=self.app.world.profile_data.cart).result_or_raise

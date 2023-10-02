from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import Label, Static

from clive.__private.core.keys import PublicKey
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.select.safe_select import SafeSelect
from clive.__private.ui.widgets.select_file_to_save_transaction import SelectFileToSaveTransaction
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.exceptions import CliveError, NoItemSelectedError
from schemas.operations.representations import Hf26OperationRepresentation, convert_to_representation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation, Transaction


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
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
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
                    yield OperationItem(
                        self.__get_operation_representation_json(operation), classes="-even" if idx % 2 == 0 else ""
                    )
            yield Static()

    @CliveScreen.try_again_after_activation()
    @on(SelectFileToSaveTransaction.Saved)
    async def save_to_file(self, event: SelectFileToSaveTransaction.Saved) -> None:
        file_path = event.file_path
        is_binary = event.binary

        signed = None
        try:
            signed = await self.__sign_transaction()
        except TransactionCouldNotBeSignedError as error:
            await self.app.world.commands.save_to_file(transaction=error.transaction, path=file_path, binary=is_binary)
        else:
            await self.app.world.commands.save_to_file(transaction=signed, path=file_path, binary=is_binary)

        self.notify(
            f"Transaction ({'binary' if is_binary else 'json'}) saved to [bold blue]'{file_path}'[/]"
            f" {'(signed)' if signed else ''}"
        )

    def action_dashboard(self) -> None:
        from clive.__private.ui.dashboard.dashboard_base import DashboardBase

        self.app.pop_screen_until(DashboardBase)

    async def action_broadcast(self) -> None:
        await self.__broadcast()

    @CliveScreen.try_again_after_activation()
    async def __broadcast(self) -> None:
        try:
            signed = await self.__sign_transaction()
        except TransactionCouldNotBeSignedError as error:
            self.notify(str(error), severity="error")
            return

        if not (await self.app.world.commands.broadcast(transaction=signed)).success:
            return

        self.__clear_all()
        self.action_dashboard()
        self.notify("Transaction broadcast successfully!")

    def action_save(self) -> None:
        self.app.push_screen(SelectFileToSaveTransaction())

    def __clear_all(self) -> None:
        self.app.world.profile_data.cart.clear()
        self.__scrollable_part.add_class("-hidden")

    async def __sign_transaction(self) -> Transaction:
        transaction = await self.__build_transaction()

        try:
            value = self.__select_key.value
        except NoItemSelectedError as error:
            raise TransactionCouldNotBeSignedError(transaction, "No key was selected!") from error
        else:
            return (await self.app.world.commands.sign(transaction=transaction, sign_with=value)).result_or_raise

    async def __build_transaction(self) -> Transaction:
        return (
            await self.app.world.commands.build_transaction(operations=self.app.world.profile_data.cart)
        ).result_or_raise

    @staticmethod
    def __get_operation_representation_json(operation: Operation) -> str:
        representation: Hf26OperationRepresentation = convert_to_representation(operation=operation)
        return representation.json(by_alias=True)

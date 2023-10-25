from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import Label, Static

from clive.__private.core.commands.sign import TransactionAlreadySignedError
from clive.__private.core.formatters import humanize
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
from schemas.operations.representations import HF26Representation, convert_to_representation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation, Transaction


class TransactionCouldNotBeSignedError(CliveError):
    def __init__(self, transaction: Transaction, reason: str = "") -> None:
        self.transaction = transaction
        super().__init__(f"Transaction could not be signed. Reason: {reason}")


class StaticPart(Static):
    """Static part of the screen."""


class ScrollablePart(ScrollableContainer, can_focus=True):
    """Scrollable part of the screen."""


class SubTitle(Label):
    DEFAULT_CSS = """
    SubTitle {
        color: $text-muted;
        text-style: bold;
        content-align: center middle;
        width: 1fr;
    }
    """


class ActionsContainer(Horizontal):
    """Container for the all the actions - combobox."""


class ActionsSpacer(Static):
    """Spacer for the actions container."""


class KeyHint(Label):
    """Hint for the authority."""


class AlreadySignedHint(Label):
    """Hint about the transaction."""

    DEFAULT_CSS = """
    AlreadySignedHint {
        margin: 1 0;
    }
    """

    def __init__(self, transaction: Transaction | None = None):
        message = (
            "(This transaction is already signed - expiration"
            f" {humanize.humanize_datetime(transaction.expiration)} UTC)"
            if transaction is not None
            else "No transaction was given"
        )
        super().__init__(message)
        self.display = transaction.is_signed() if transaction is not None else False


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

    def __init__(self, *, loaded_transaction: Transaction | None = None) -> None:
        super().__init__()

        self.__loaded_transaction = loaded_transaction
        self.__scrollable_part = ScrollablePart()
        self.__select_key = SelectKey()

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            with StaticPart():
                yield BigTitle("transaction summary")
                yield SubTitle("(Loaded from file)" if self.__loaded_transaction else "(Built from cart)")
                with ActionsContainer():
                    if not self.__has_loaded_signed_transaction():
                        yield KeyHint("Sign with key:")
                        yield self.__select_key
                    yield AlreadySignedHint(self.__loaded_transaction)

                yield TransactionHint("This transaction will contain following operations in the presented order:")
            with self.__scrollable_part:
                for idx, operation in enumerate(self.__get_operations()):
                    yield OperationItem(
                        self.__get_operation_representation_json(operation), classes="-even" if idx % 2 == 0 else ""
                    )
            yield Static()

    @CliveScreen.try_again_after_activation()
    @on(SelectFileToSaveTransaction.Saved)
    async def save_to_file(self, event: SelectFileToSaveTransaction.Saved) -> None:
        file_path = event.file_path
        should_be_binary = event.binary
        should_be_signed = event.signed and not self.__has_loaded_signed_transaction()

        transaction = await self.__get_transaction()

        if should_be_signed:
            tx = await self.__try_to_sign_transaction(transaction)
            if tx is None:
                return
            transaction = tx

        assert transaction is not None, "Transaction should be built at this point!"
        await self.app.world.commands.save_to_file(transaction=transaction, path=file_path, binary=should_be_binary)

        self.notify(
            f"Transaction ({'binary' if should_be_binary else 'json'}) saved to [bold green]'{file_path}'[/]"
            f" {'(signed)' if transaction.is_signed() else ''}"
        )

    def action_dashboard(self) -> None:
        from clive.__private.ui.dashboard.dashboard_base import DashboardBase

        self.app.pop_screen_until(DashboardBase)

    async def action_broadcast(self) -> None:
        await self.__broadcast()

    @CliveScreen.try_again_after_activation()
    async def __broadcast(self) -> None:
        transaction = await self.__get_transaction()

        if not transaction.is_signed():
            tx = await self.__try_to_sign_transaction(transaction)
            if tx is None:
                return
            transaction = tx

        if not (await self.app.world.commands.broadcast(transaction=transaction)).success:
            return

        if not self.__loaded_transaction:
            self.__clear_all()
        self.action_dashboard()
        self.notify("Transaction broadcast successfully!")

    def action_save(self) -> None:
        self.app.push_screen(SelectFileToSaveTransaction(already_signed=self.__has_loaded_signed_transaction()))

    def __has_loaded_signed_transaction(self) -> bool:
        return self.__loaded_transaction is not None and self.__loaded_transaction.is_signed()

    def __clear_all(self) -> None:
        self.app.world.profile_data.cart.clear()
        self.__scrollable_part.add_class("-hidden")

    async def __sign_transaction(self, transaction: Transaction) -> Transaction:
        try:
            value = self.__select_key.value
        except NoItemSelectedError as error:
            raise TransactionCouldNotBeSignedError(transaction, "No key was selected!") from error

        try:
            return (await self.app.world.commands.sign(transaction=transaction, sign_with=value)).result_or_raise
        except TransactionAlreadySignedError as error:
            raise TransactionCouldNotBeSignedError(transaction, "Transaction is already signed!") from error

    async def __build_transaction(self) -> Transaction:
        return (
            await self.app.world.commands.build_transaction(operations=self.app.world.profile_data.cart)
        ).result_or_raise

    async def __try_to_sign_transaction(self, transaction: Transaction) -> Transaction | None:
        try:
            return await self.__sign_transaction(transaction)
        except TransactionCouldNotBeSignedError as error:
            self.notify(str(error), severity="error")
            return None

    async def __get_transaction(self) -> Transaction:
        return self.__loaded_transaction or await self.__build_transaction()

    def __get_operations(self) -> list[Operation | HF26Representation[Operation]]:
        if self.__loaded_transaction:
            return self.__loaded_transaction.operations
        return list(self.app.world.profile_data.cart)

    @staticmethod
    def __get_operation_representation_json(operation: Operation | HF26Representation[Operation]) -> str:
        representation: HF26Representation[Operation] = convert_to_representation(operation=operation)
        return representation.json(by_alias=True)

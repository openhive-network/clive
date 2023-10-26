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
from clive.exceptions import CliveError, NoItemSelectedError
from schemas.operations.representations import HF26Representation, convert_to_representation

if TYPE_CHECKING:
    from rich.console import RenderableType
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


class TransactionMetadataContainer(Horizontal):
    """Container for the transaction metadata."""


class ContainerTitle(Static):
    """A title for the container."""


class TransactionContentHint(Label):
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


class KeyHint(Label):
    """Hint for the authority."""


class TransactionSummaryCommon(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__, name="common")]
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
        Binding("f2", "save", "Save"),
        Binding("f3", "dashboard", "Dashboard"),
        Binding("f10", "broadcast", "Broadcast"),
    ]

    def __init__(self, transaction: Transaction | None = None) -> None:
        super().__init__()

        self._transaction = transaction
        self.__transaction_metadata_container = TransactionMetadataContainer()
        self.__scrollable_part = ScrollablePart()
        self._select_key = SelectKey()

    @property
    def transaction(self) -> Transaction:
        assert self._transaction is not None, "Transaction should be initialized at this point!"
        return self._transaction

    @property
    def operations(self) -> list[Operation]:
        return self.transaction.operations_models

    async def on_mount(self) -> None:
        if not self._transaction:
            self._transaction = await self._initialize_transaction()

        await self.__mount_transaction_metadata()
        await self.__mount_operation_items()

    async def _initialize_transaction(self) -> Transaction:
        """Should return transaction that will be used in further actions."""
        raise NotImplementedError("Transaction not passed via constructor and _initialize_transaction not implemented!")

    def _get_subtitle(self) -> RenderableType:
        return ""

    def create_main_panel(self) -> ComposeResult:
        with StaticPart():
            yield BigTitle("transaction summary")
            yield SubTitle(self._get_subtitle())
            yield ContainerTitle("TRANSACTION METADATA")
            yield self.__transaction_metadata_container
            with ActionsContainer():
                yield from self._actions_container_content()
            yield TransactionContentHint("This transaction will contain following operations in the presented order:")
        yield self.__scrollable_part
        yield Static()

    def _actions_container_content(self) -> ComposeResult:
        yield KeyHint("Sign with key:")
        yield self._select_key

    async def __mount_transaction_metadata(self) -> None:
        expiration = humanize.humanize_datetime(self.transaction.expiration)
        things_to_mount = [
            Label(f"Ref block num: {self.transaction.ref_block_num}"),
            Label(f"Expiration: {expiration}"),
            Label(f"Hash: {self.transaction.calculate_transaction_id()}"),
        ]
        await self.__transaction_metadata_container.mount_all(things_to_mount)

    async def __mount_operation_items(self) -> None:
        things_to_mount = []
        for idx, operation in enumerate(self.operations):
            operation_item = OperationItem(
                self.__get_operation_representation_json(operation), classes="-even" if idx % 2 == 0 else ""
            )
            things_to_mount.append(operation_item)
        await self.__scrollable_part.mount_all(things_to_mount)

    @CliveScreen.try_again_after_activation()
    @on(SelectFileToSaveTransaction.Saved)
    async def save_to_file(self, event: SelectFileToSaveTransaction.Saved) -> None:
        file_path = event.file_path
        save_as_binary = event.save_as_binary
        should_be_signed = event.should_be_signed

        transaction = self.transaction

        if should_be_signed:
            tx = await self.__try_to_sign_transaction(transaction)
            if tx is None:
                return
            transaction = tx

        assert transaction is not None, "Transaction should be built at this point!"
        await self.app.world.commands.save_to_file(transaction=transaction, path=file_path, binary=save_as_binary)

        self.notify(
            f"Transaction ({'binary' if save_as_binary else 'json'}) saved to [bold green]'{file_path}'[/]"
            f" {'(signed)' if transaction.is_signed() else ''}"
        )

    def action_dashboard(self) -> None:
        from clive.__private.ui.dashboard.dashboard_base import DashboardBase

        self.app.pop_screen_until(DashboardBase)

    async def action_broadcast(self) -> None:
        await self.__broadcast()

    @CliveScreen.try_again_after_activation()
    async def __broadcast(self) -> None:
        transaction = self.transaction

        if not transaction.is_signed():
            tx = await self.__try_to_sign_transaction(transaction)
            if tx is None:
                return
            transaction = tx

        if not (await self.app.world.commands.broadcast(transaction=transaction)).success:
            return

        self.action_dashboard()
        self.notify("Transaction broadcast successfully!")
        self._actions_after_successful_broadcast()

    def _actions_after_successful_broadcast(self) -> None:
        """Actions that should be performed after the transaction is broadcasted."""

    def action_save(self) -> None:
        self.app.push_screen(SelectFileToSaveTransaction())

    async def __sign_transaction(self, transaction: Transaction) -> Transaction:
        try:
            value = self._select_key.value
        except NoItemSelectedError as error:
            raise TransactionCouldNotBeSignedError(transaction, "No key was selected!") from error

        try:
            return (await self.app.world.commands.sign(transaction=transaction, sign_with=value)).result_or_raise
        except TransactionAlreadySignedError as error:
            raise TransactionCouldNotBeSignedError(transaction, "Transaction is already signed!") from error

    async def __try_to_sign_transaction(self, transaction: Transaction) -> Transaction | None:
        try:
            return await self.__sign_transaction(transaction)
        except TransactionCouldNotBeSignedError as error:
            self.notify(str(error), severity="error")
            return None

    @staticmethod
    def __get_operation_representation_json(operation: Operation) -> str:
        representation: HF26Representation[Operation] = convert_to_representation(operation=operation)
        return representation.json(by_alias=True)

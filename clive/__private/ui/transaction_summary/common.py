from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Label, Select, Static

from clive.__private.core.commands.abc.command_in_unlocked import CommandRequiresUnlockedModeError
from clive.__private.core.formatters import humanize
from clive.__private.core.keys import PublicKey
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.models.aliased import convert_to_representation
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.scrolling import ScrollablePartFocusable
from clive.__private.ui.widgets.select.safe_select import SafeSelect
from clive.__private.ui.widgets.select_file_to_save_transaction import SelectFileToSaveTransaction
from clive.exceptions import NoItemSelectedError

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult
    from textual.widgets._select import NoSelection

    from clive.__private.models import Transaction
    from clive.__private.models.aliased import OperationRepresentationBase, OperationUnion


class StaticPart(Container):
    """Static part of the screen."""


class ActionsContainer(Horizontal):
    """Container for the all the actions - combobox."""


class TransactionMetadataContainer(Horizontal):
    """Container for the transaction metadata."""

    BORDER_TITLE = "TRANSACTION METADATA"


class TaposHolder(Vertical):
    """Container for the TaPoS metadata."""

    def __init__(self, ref_block_num: int, ref_block_prefix: int) -> None:
        super().__init__()
        self.__ref_block_num = ref_block_num
        self.__ref_block_prefix = ref_block_prefix

    def compose(self) -> ComposeResult:
        yield Label("TaPoS:")
        yield Label(f"Ref block num: {self.__ref_block_num}", id="ref-block-num")
        yield Label(f"Ref block prefix: {self.__ref_block_prefix}", id="ref-block-prefix")


class TransactionContentHint(Label):
    """Hint about the transaction."""


class OperationItem(Static):
    """Item in the operations list."""


class SelectKey(SafeSelect[PublicKey], CliveWidget):
    """Combobox for selecting the public key."""

    def __init__(self) -> None:
        try:
            first_value: PublicKey | NoSelection = self.profile.keys.first
        except KeyNotFoundError:
            first_value = Select.BLANK

        super().__init__(
            [(key.alias, key) for key in self.profile.keys],
            value=first_value,
            empty_string="no private key found",
        )


class KeyHint(Label):
    """Hint for the key."""


class TransactionSummaryCommon(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__, name="common")]
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("f2", "save", "Save"),
        Binding("f3", "dashboard", "Dashboard"),
        Binding("f6", "broadcast", "Broadcast"),
    ]
    BIG_TITLE = "transaction summary"

    def __init__(self, transaction: Transaction | None = None) -> None:
        super().__init__()

        self._transaction = transaction
        self.__transaction_metadata_container = TransactionMetadataContainer()
        self.__scrollable_part = ScrollablePartFocusable()
        self._select_key = SelectKey()

    @property
    def transaction(self) -> Transaction:
        assert self._transaction is not None, "Transaction should be initialized at this point!"
        return self._transaction

    @property
    def operations(self) -> list[OperationUnion]:
        return self.transaction.operations_models

    async def on_mount(self) -> None:
        if not self._transaction:
            self._transaction = await self._initialize_transaction()

        await self.__mount_transaction_metadata()
        await self.__mount_operation_items()

    async def _initialize_transaction(self) -> Transaction:
        """Return transaction that will be used in further actions."""
        raise NotImplementedError("Transaction not passed via constructor and _initialize_transaction not implemented!")

    def _get_subtitle(self) -> RenderableType:
        return ""

    def create_main_panel(self) -> ComposeResult:
        with StaticPart():
            yield self.__transaction_metadata_container
            with ActionsContainer():
                yield from self._actions_container_content()
            yield TransactionContentHint("This transaction will contain following operations in the presented order:")
        yield self.__scrollable_part

    def _actions_container_content(self) -> ComposeResult:
        yield KeyHint("Sign with key:")
        yield self._select_key

    async def __mount_transaction_metadata(self) -> None:
        expiration = humanize.humanize_datetime(self.transaction.expiration)
        things_to_mount = [
            TaposHolder(self.transaction.ref_block_num, self.transaction.ref_block_prefix),
            Label(f"Expiration: {expiration}"),
            Label(f"Transaction ID: {self.transaction.calculate_transaction_id()}"),
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

    @CliveScreen.try_again_after_unlock
    @on(SelectFileToSaveTransaction.Saved)
    async def save_to_file(self, event: SelectFileToSaveTransaction.Saved) -> None:
        file_path = event.file_path
        save_as_binary = event.save_as_binary
        should_be_signed = event.should_be_signed

        transaction = self.transaction.copy()

        try:
            transaction = (
                await self.commands.perform_actions_on_transaction(
                    content=transaction,
                    sign_key=self.__get_key_to_sign() if should_be_signed else None,
                    force_unsign=not should_be_signed,
                    save_file_path=file_path,
                    force_save_format="bin" if save_as_binary else "json",
                )
            ).result_or_raise
        except CommandRequiresUnlockedModeError:
            raise  # reraise so try_again_after_unlock decorator can handle it
        except Exception as error:  # noqa: BLE001
            self.notify(f"Transaction save failed. Reason: {error}", severity="error")
            return

        self.notify(
            f"Transaction ({'binary' if save_as_binary else 'json'}) saved to [bold green]'{file_path}'[/]"
            f" {'(signed)' if transaction.is_signed() else ''}"
        )

    def action_dashboard(self) -> None:
        from clive.__private.ui.dashboard.dashboard_base import DashboardBase

        self.app.pop_screen_until(DashboardBase)

    async def action_broadcast(self) -> None:
        await self.__broadcast()

    @CliveScreen.try_again_after_unlock
    async def __broadcast(self) -> None:
        transaction = self.transaction

        try:
            (
                await self.commands.perform_actions_on_transaction(
                    content=transaction,
                    sign_key=self.__get_key_to_sign() if not transaction.is_signed() else None,
                    broadcast=True,
                )
            ).raise_if_error_occurred()
        except CommandRequiresUnlockedModeError:
            raise  # reraise so try_again_after_unlock decorator can handle it
        except Exception as error:  # noqa: BLE001
            self.notify(f"Transaction broadcast failed! Reason: {error}", severity="error")
            return

        self.action_dashboard()
        self.notify(f"Transaction with ID '{transaction.calculate_transaction_id()}' successfully broadcasted!")
        self._actions_after_successful_broadcast()

    def _actions_after_successful_broadcast(self) -> None:
        """Actions that should be performed after the transaction is broadcasted."""

    def action_save(self) -> None:
        self.app.push_screen(SelectFileToSaveTransaction())

    def __get_key_to_sign(self) -> PublicKey:
        try:
            return self._select_key.value
        except NoItemSelectedError as error:
            raise NoItemSelectedError("No key was selected!") from error

    @staticmethod
    def __get_operation_representation_json(operation: OperationUnion) -> str:
        representation: OperationRepresentationBase = convert_to_representation(operation=operation)
        return representation.json(by_alias=True)

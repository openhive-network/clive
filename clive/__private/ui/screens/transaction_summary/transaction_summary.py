from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Label, Select

from clive.__private.core.commands.abc.command_in_unlocked import CommandRequiresUnlockedModeError
from clive.__private.core.commands.load_transaction import LoadTransactionError
from clive.__private.core.keys import PublicKey
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.transaction_summary.cart_table import CartTable
from clive.__private.ui.screens.transaction_summary.transaction_metadata_container import TransactionMetadataContainer
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.select.safe_select import SafeSelect
from clive.__private.ui.widgets.select_file import SaveFileResult, SelectFile
from clive.__private.ui.widgets.select_file_to_save_transaction import (
    SaveTransactionResult,
    SelectFileToSaveTransaction,
)

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widgets._select import NoSelection

    from clive.__private.models import Transaction


class ButtonBroadcast(CliveButton):
    """Button used to broadcasting transaction."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that broadcast button was pressed."""

    def __init__(self) -> None:
        super().__init__("Broadcast (F6)", variant="success")


class ButtonContainer(Horizontal):
    """Container for storing ButtonBroadcast, ButtonOpenTransactionFromFile and ButtonSave."""

    transaction: Transaction | None = reactive(None, recompose=True)  # type: ignore[assignment]

    def __init__(self, transaction: Transaction | None) -> None:
        super().__init__()
        self.transaction = transaction

    def compose(self) -> ComposeResult:
        yield ButtonBroadcast() if self.transaction else ButtonOpenTransactionFromFile()
        if self.transaction:
            yield ButtonSave()


class ButtonSave(CliveButton):
    """Button used to save transaction to file."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that save button was pressed."""

    def __init__(self) -> None:
        super().__init__("Save to file (F2)")


class ButtonOpenTransactionFromFile(CliveButton):
    """Button used to load transaction from file."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that open from file button was pressed."""

    def __init__(self) -> None:
        super().__init__("Open from file (F3)")


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


class TransactionSummary(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("f3", "load_transaction_from_file", "Open transaction file"),
        Binding("f6", "broadcast", "Broadcast"),
        Binding("f2", "save_to_file", "Save to file"),
    ]
    BIG_TITLE = "transaction summary"

    def __init__(self, transaction: Transaction | None) -> None:
        super().__init__()
        self._transaction = transaction
        self._transaction_metadata_container = TransactionMetadataContainer(transaction)
        self._button_container = ButtonContainer(transaction)
        self._select_key = SelectKey()

    @property
    def transaction(self) -> Transaction:
        assert self._transaction is not None, "Transaction should be initialized at this point!"
        return self._transaction

    @property
    def button_save(self) -> CliveButton:
        return self.query_one(ButtonSave)

    def create_main_panel(self) -> ComposeResult:
        yield self._transaction_metadata_container
        with Horizontal(id="actions-container"):
            yield KeyHint("Sign with key:")
            yield self._select_key
            yield self._button_container
        with ScrollablePart():
            yield CartTable()

    async def on_mount(self) -> None:
        await self._handle_bindings()

    @on(ButtonOpenTransactionFromFile.Pressed)
    def action_load_transaction_from_file(self) -> None:
        notify_text = "Loading transaction from file will clear current cart content." if self.profile.cart else None
        self.app.push_screen(SelectFile(notice=notify_text), self._load_transaction_from_file)

    @on(ButtonBroadcast.Pressed)
    async def action_broadcast(self) -> None:
        await self._broadcast()

    @on(ButtonSave.Pressed)
    def action_save_to_file(self) -> None:
        self.app.push_screen(SelectFileToSaveTransaction(), self._save_to_file)

    @on(CartTable.Modified)
    async def transaction_modified(self) -> None:
        self._transaction = await self._build_transaction() if self.profile.cart else None
        self._transaction_metadata_container.transaction = self._transaction
        self._button_container.transaction = self._transaction
        await self._handle_bindings()

    @CliveScreen.try_again_after_unlock
    async def _save_to_file(self, result: SaveTransactionResult) -> None:
        file_path = result.file_path
        save_as_binary = result.save_as_binary
        should_be_signed = result.should_be_signed
        transaction = self.transaction.copy()
        try:
            transaction = (
                await self.commands.perform_actions_on_transaction(
                    content=transaction,
                    sign_key=self._get_key_to_sign() if should_be_signed else None,
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

    async def _load_transaction_from_file(self, result: SaveFileResult) -> None:
        file_path = result.file_path

        try:
            loaded_transaction = (await self.commands.load_transaction_from_file(path=file_path)).result_or_raise
        except LoadTransactionError as error:
            self.notify(f"Error occurred while loading transaction from file: {error}", severity="error")
            return
        self._transaction = loaded_transaction
        self._transaction_metadata_container.transaction = self._transaction
        self._button_container.transaction = self._transaction
        if not self.transaction.is_tapos_set():
            self.notify("TaPoS metadata was not set, updating automatically...")
            await self.commands.update_transaction_metadata(transaction=self.transaction)

        self.profile.cart.fill_from_transaction(self.transaction)
        self.app.trigger_profile_watchers()
        await self.query_one(CartTable).rebuild()

    @CliveScreen.try_again_after_unlock
    async def _broadcast(self) -> None:
        from clive.__private.ui.screens.dashboard import DashboardBase

        transaction = self.transaction
        try:
            (
                await self.commands.perform_actions_on_transaction(
                    content=transaction,
                    sign_key=self._get_key_to_sign() if not transaction.is_signed() else None,
                    broadcast=True,
                )
            ).raise_if_error_occurred()
        except CommandRequiresUnlockedModeError:
            raise  # reraise so try_again_after_unlock decorator can handle it
        except Exception as error:  # noqa: BLE001
            self.notify(f"Transaction broadcast failed! Reason: {error}", severity="error")
            return
        self.profile.cart.clear()
        self.notify(f"Transaction with ID '{transaction.calculate_transaction_id()}' successfully broadcasted!")
        self.app.pop_screen_until(DashboardBase)

    async def _build_transaction(self) -> Transaction:
        return (await self.commands.build_transaction(content=self.profile.cart)).result_or_raise

    def _get_key_to_sign(self) -> PublicKey:
        return self._select_key.value

    async def _handle_bindings(self) -> None:
        if not self._transaction:
            self.unbind("f6")
            self.unbind("f2")
        else:
            self.bind(Binding("f6", "broadcast", "Broadcast"))
            self.bind(Binding("f2", "save_to_file", "Save to file"))

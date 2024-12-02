from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Label, Select, Static

from clive.__private.core.commands.load_transaction import LoadTransactionError
from clive.__private.core.keys import PublicKey
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.transaction_summary.cart_table import CartTable
from clive.__private.ui.screens.transaction_summary.transaction_metadata_container import TransactionMetadataContainer
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.notice import Notice
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.select.safe_select import SafeSelect
from clive.__private.ui.widgets.select_file import SaveFileResult, SelectFile
from clive.__private.ui.widgets.select_file_to_save_transaction import (
    SaveTransactionResult,
    SelectFileToSaveTransaction,
)
from clive.exceptions import NoItemSelectedError

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult
    from textual.widgets._select import NoSelection

    from clive.__private.models import Transaction


class AlreadySignedHint(Label):
    """Hint about the already signed transaction."""

    DEFAULT_CSS = """
    AlreadySignedHint {
        margin: 1 0;
        color: $success;
    }
    """

    def __init__(self) -> None:
        super().__init__("(This transaction is already signed)")


class ButtonBroadcast(CliveButton):
    """Button used to broadcasting transaction."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that broadcast button was pressed."""

    def __init__(self) -> None:
        super().__init__("Broadcast (F6)", variant="success")


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


class ButtonContainer(Horizontal):
    """Container for storing ButtonBroadcast, ButtonOpenTransactionFromFile and ButtonSave."""

    transaction: Transaction | None = reactive(None, recompose=True)  # type: ignore[assignment]

    def __init__(self, transaction: Transaction | None) -> None:
        super().__init__()
        self.transaction = transaction

    def compose(self) -> ComposeResult:
        if self.transaction:
            yield ButtonBroadcast()
            yield ButtonSave()
        else:
            yield ButtonOpenTransactionFromFile()


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


class Subtitle(Static):
    """Used to display file path when transaction is loaded."""


class KeyHint(Label):
    """Hint for the key."""


class KeyContainer(Horizontal):
    """Container for storing widgets connected with keys."""

    transaction: Transaction | None = reactive(None, recompose=True)  # type: ignore[assignment]

    def __init__(self, transaction: Transaction | None) -> None:
        super().__init__()
        self.transaction = transaction

    @property
    def selected_key(self) -> PublicKey:
        """
        Return selected key.

        Raises
        ------
        NoItemSelectedError: When no key was selected.
        """
        select_key = self.query_exactly_one(SelectKey)
        try:
            return select_key.value
        except NoItemSelectedError as error:
            raise NoItemSelectedError("No key was selected!") from error

    def compose(self) -> ComposeResult:
        if self.transaction and self.transaction.is_signed():
            yield AlreadySignedHint()
        else:
            yield KeyHint("Sign with key:")
            yield SelectKey()


class TransactionSummary(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("f3", "load_transaction_from_file", "Open transaction file"),
        Binding("f6", "broadcast", "Broadcast"),
        Binding("f2", "save_to_file", "Save to file"),
    ]
    BIG_TITLE = "transaction summary"
    transaction: Transaction | None = reactive(None, init=False)  # type: ignore[assignment]

    def __init__(self, transaction: Transaction | None) -> None:
        super().__init__()
        self.set_reactive(self.__class__.transaction, transaction)  # type: ignore[arg-type]
        self._transaction_file_path: Path | None = None

    @property
    def transaction_ensure(self) -> Transaction:
        assert self.transaction is not None, "Transaction should be initialized at this point!"
        return self.transaction

    @property
    def button_save(self) -> CliveButton:
        return self.query_exactly_one(ButtonSave)

    @property
    def key_container(self) -> KeyContainer:
        return self.query_exactly_one(KeyContainer)

    @property
    def _should_display_warning_notice(self) -> bool:
        return self.transaction is not None and self.transaction.is_signed()

    def create_main_panel(self) -> ComposeResult:
        yield Subtitle()
        yield TransactionMetadataContainer(self.transaction)

        notice = Notice(
            "If you leave this screen or edit the transaction, the signatures will be lost and the transaction "
            "metadata will be recalculated.",
        )
        notice.display = self._should_display_warning_notice
        yield notice
        with Horizontal(id="actions-container"):
            key_container = KeyContainer(self.transaction)
            key_container.display = bool(self.transaction)
            yield key_container
            yield ButtonContainer(self.transaction)
        with ScrollablePart():
            yield CartTable()

    def on_mount(self) -> None:
        self._handle_bindings()

    @on(ButtonOpenTransactionFromFile.Pressed)
    def action_load_transaction_from_file(self) -> None:
        notify_text = (
            "Loading the transaction from the file will clear the current content of the cart."
            if self.profile.cart
            else None
        )
        self.app.push_screen(SelectFile(notice=notify_text), self._load_transaction_from_file)

    @on(ButtonBroadcast.Pressed)
    async def action_broadcast(self) -> None:
        await self._broadcast()

    @on(ButtonSave.Pressed)
    def action_save_to_file(self) -> None:
        self.app.push_screen(SelectFileToSaveTransaction(), self._save_to_file)

    @on(CartTable.Modified)
    async def handle_cart_update(self) -> None:
        self._transaction_file_path = None
        self.transaction = await self._build_transaction() if self.profile.cart else None

    def watch_transaction(self, transaction: Transaction | None) -> None:
        self.query_exactly_one(TransactionMetadataContainer).transaction = transaction
        self.query_exactly_one(ButtonContainer).transaction = transaction
        self.key_container.transaction = transaction
        self.key_container.display = bool(transaction)
        self.query_exactly_one(Notice).display = self._should_display_warning_notice
        subtitle = self.query_exactly_one(Subtitle)
        if self._transaction_file_path:
            subtitle.update(f"Loaded from [blue]{self._transaction_file_path}[/]")
        subtitle.display = bool(self._transaction_file_path)
        self._handle_bindings()

    async def _save_to_file(self, result: SaveTransactionResult | None) -> None:
        if result is None:
            return

        file_path = result.file_path
        save_as_binary = result.save_as_binary
        should_be_signed = result.should_be_signed
        transaction = self.transaction_ensure.copy()
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
        except Exception as error:  # noqa: BLE001
            self.notify(f"Transaction save failed. Reason: {error}", severity="error")
            return
        self.profile.cart.clear()
        await self.handle_cart_update()
        await self.query_exactly_one(CartTable).rebuild()
        self.notify(
            f"Transaction ({'binary' if save_as_binary else 'json'}) saved to [bold green]'{file_path}'[/]"
            f" {'(signed)' if transaction.is_signed() else ''}"
        )

    async def _load_transaction_from_file(self, result: SaveFileResult | None) -> None:
        if result is None:
            return

        file_path = result.file_path

        try:
            loaded_transaction = (await self.commands.load_transaction_from_file(path=file_path)).result_or_raise
        except LoadTransactionError as error:
            self.notify(f"Error occurred while loading transaction from file: {error}", severity="error")
            return
        self._transaction_file_path = file_path
        self.transaction = loaded_transaction

        if not self.transaction.is_tapos_set():
            self.notify("TaPoS metadata was not set, updating automatically...")
            await self.commands.update_transaction_metadata(transaction=self.transaction)

        self.profile.cart.fill_from_transaction(self.transaction)
        self.app.trigger_profile_watchers()
        await self.query_exactly_one(CartTable).rebuild()

    async def _broadcast(self) -> None:
        from clive.__private.ui.screens.dashboard import Dashboard

        transaction = self.transaction_ensure
        try:
            (
                await self.commands.perform_actions_on_transaction(
                    content=transaction,
                    sign_key=self._get_key_to_sign() if not transaction.is_signed() else None,
                    broadcast=True,
                )
            ).raise_if_error_occurred()
        except Exception as error:  # noqa: BLE001
            self.notify(f"Transaction broadcast failed! Reason: {error}", severity="error")
            return

        self.profile.cart.clear()
        self.notify(f"Transaction with ID '{transaction.calculate_transaction_id()}' successfully broadcasted!")
        self.app.get_screen_from_current_stack(Dashboard).pop_until_active()

    async def _build_transaction(self) -> Transaction:
        return (await self.commands.build_transaction(content=self.profile.cart)).result_or_raise

    def _get_key_to_sign(self) -> PublicKey:
        return self.key_container.selected_key

    def _handle_bindings(self) -> None:
        if not self.transaction:
            self.unbind("f6")
            self.unbind("f2")
        else:
            self.bind(Binding("f6", "broadcast", "Broadcast"))
            self.bind(Binding("f2", "save_to_file", "Save to file"))

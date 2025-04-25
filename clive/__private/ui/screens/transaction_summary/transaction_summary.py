from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Label, Select, Static

from clive.__private.core.commands.load_transaction import LoadTransactionError
from clive.__private.core.constants.tui.bindings import (
    BROADCAST_TRANSACTION_BINDING_KEY,
    LOAD_TRANSACTION_FROM_FILE_BINDING_KEY,
    REFRESH_TRANSACTION_METADATA_BINDING_KEY,
    SAVE_TRANSACTION_TO_FILE_BINDING_KEY,
)
from clive.__private.core.keys import PublicKey
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs import ConfirmInvalidateSignaturesDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.transaction_summary.cart_table import CartTable
from clive.__private.ui.screens.transaction_summary.transaction_metadata_container import (
    RefreshMetadataButton,
    TransactionMetadataContainer,
)
from clive.__private.ui.styling import colorize_path
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.select.safe_select import SafeSelect
from clive.__private.ui.widgets.select_file import SaveFileResult, SelectFile
from clive.__private.ui.widgets.select_file_to_save_transaction import (
    SaveTransactionResult,
    SelectFileToSaveTransaction,
)
from clive.__private.visitors.operation.potential_known_account_visitor import PotentialKnownAccountCollector
from clive.exceptions import NoItemSelectedError

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widgets._select import NoSelection


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
        super().__init__(f"Broadcast ({BROADCAST_TRANSACTION_BINDING_KEY.upper()})", variant="success")


class ButtonSave(CliveButton):
    """Button used to save transaction to file."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that save button was pressed."""

    def __init__(self) -> None:
        super().__init__(f"Save to file ({SAVE_TRANSACTION_TO_FILE_BINDING_KEY.upper()})")


class ButtonOpenTransactionFromFile(CliveButton):
    """Button used to load transaction from file."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that open from file button was pressed."""

    def __init__(self) -> None:
        super().__init__(f"Open from file ({LOAD_TRANSACTION_FROM_FILE_BINDING_KEY.upper()})")


class ButtonContainer(Horizontal, CliveWidget):
    """Container for storing ButtonBroadcast, ButtonOpenTransactionFromFile and ButtonSave."""

    def compose(self) -> ComposeResult:
        if self.profile.transaction:
            yield ButtonSave()
            yield ButtonOpenTransactionFromFile()
            yield ButtonBroadcast()
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


class KeyContainer(Horizontal, CliveWidget):
    """Container for storing widgets connected with keys."""

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
        if self.profile.transaction.is_signed:
            yield AlreadySignedHint()
        else:
            yield KeyHint("Sign with key:")
            yield SelectKey()
        self.display = bool(self.profile.transaction)


class TransactionSummary(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding(LOAD_TRANSACTION_FROM_FILE_BINDING_KEY, "load_transaction_from_file", "Open transaction file"),
        Binding(BROADCAST_TRANSACTION_BINDING_KEY, "broadcast", "Broadcast"),
        Binding(SAVE_TRANSACTION_TO_FILE_BINDING_KEY, "save_to_file", "Save to file"),
        Binding(REFRESH_TRANSACTION_METADATA_BINDING_KEY, "refresh_metadata", "Refresh metadata"),
    ]
    BIG_TITLE = "transaction summary"

    def __init__(self) -> None:
        super().__init__()
        self._update_bindings()

    @property
    def key_container(self) -> KeyContainer:
        return self.query_exactly_one(KeyContainer)

    @property
    def button_container(self) -> ButtonContainer:
        return self.query_exactly_one(ButtonContainer)

    @property
    def transaction_metadata_container(self) -> TransactionMetadataContainer:
        return self.query_exactly_one(TransactionMetadataContainer)

    def create_main_panel(self) -> ComposeResult:
        yield Subtitle(self._create_subtitle_content())
        yield TransactionMetadataContainer()
        with Horizontal(id="actions-container"):
            key_container = KeyContainer()
            yield key_container
            yield ButtonContainer()
        with ScrollablePart():
            yield CartTable()

    @on(ButtonOpenTransactionFromFile.Pressed)
    def action_load_transaction_from_file(self) -> None:
        notify_text = (
            "Loading the transaction from the file will clear the current content of the cart."
            if self.profile.transaction
            else None
        )
        self.app.push_screen(SelectFile(notice=notify_text), self._load_transaction_from_file)

    @on(ButtonBroadcast.Pressed)
    async def action_broadcast(self) -> None:
        await self._broadcast()

    @on(ButtonSave.Pressed)
    def action_save_to_file(self) -> None:
        self.app.push_screen(SelectFileToSaveTransaction(), self._save_to_file)

    @on(RefreshMetadataButton.Pressed)
    async def action_refresh_metadata(self) -> None:
        async def refresh() -> None:
            await self._update_transaction_metadata()
            await self._rebuild_signatures_changed()
            self._update_subtitle()

        async def refresh_metadata_cb(confirm: bool | None) -> None:
            if confirm:
                await refresh()

        if self.profile.transaction.is_signed:
            await self.app.push_screen(ConfirmInvalidateSignaturesDialog(), refresh_metadata_cb)
        else:
            await refresh()

    @on(CartTable.Modified)
    async def handle_cart_update(self) -> None:
        await self._update_transaction_metadata()
        await self._rebuild_signatures_changed()
        await self.button_container.recompose()
        self._update_subtitle()
        self._update_bindings()

    def _create_subtitle_content(self) -> str:
        if self.profile.transaction_file_path:
            return f"Loaded from {colorize_path(self.profile.transaction_file_path)}"
        return ""

    async def _save_to_file(self, result: SaveTransactionResult | None) -> None:
        if result is None:
            return

        file_path = result.file_path
        save_as_binary = result.save_as_binary
        should_be_signed = result.should_be_signed
        transaction = self.profile.transaction.copy()

        try:
            sign_key = self._get_key_to_sign() if should_be_signed and not transaction.is_signed else None
        except NoItemSelectedError:
            self.notify("Transaction can't be saved because no key was selected.", severity="error")
            return

        wrapper = await self.commands.perform_actions_on_transaction(
            content=transaction,
            sign_key=sign_key,
            force_unsign=not should_be_signed,
            save_file_path=file_path,
            force_save_format="bin" if save_as_binary else "json",
        )

        if wrapper.error_occurred:
            self.notify("Transaction save failed. Please try again.", severity="error")
            return

        self.profile.transaction.reset()
        self.profile.transaction_file_path = None
        self.app.trigger_profile_watchers()
        await self._rebuild()
        self.notify(
            f"Transaction ({'binary' if save_as_binary else 'json'}) saved to {colorize_path(file_path)}"
            f" {'(signed)' if transaction.is_signed else ''}"
        )

    def _add_known_accounts(self) -> None:
        visitor = PotentialKnownAccountCollector()
        self.profile.transaction.accept(visitor)
        unknown_accounts = visitor.get_unknown_accounts(self.profile.accounts.known)
        self.profile.accounts.add_known_account(*unknown_accounts)
        if unknown_accounts:
            accounts = ", ".join(unknown_accounts)
            self.notify(f"New accounts have been added to the list of known accounts: {accounts}.")

    async def _load_transaction_from_file(self, result: SaveFileResult | None) -> None:
        if result is None:
            return

        file_path = result.file_path

        try:
            loaded_transaction = (await self.commands.load_transaction_from_file(path=file_path)).result_or_raise
        except LoadTransactionError as error:
            self.notify(f"Error occurred while loading transaction from file: {error}", severity="error")
            return

        if not loaded_transaction.is_tapos_set:
            self.notify("TaPoS metadata was not set, updating automatically...")
            await self._update_transaction_metadata()

        self.profile.transaction_file_path = file_path
        self.profile.transaction = loaded_transaction
        if self.profile.should_enable_known_accounts:
            self._add_known_accounts()
        self.app.trigger_profile_watchers()
        await self._rebuild()

    async def _broadcast(self) -> None:
        from clive.__private.ui.screens.dashboard import Dashboard

        transaction = self.profile.transaction

        try:
            sign_key = self._get_key_to_sign() if not transaction.is_signed else None
        except NoItemSelectedError:
            self.notify("Transaction can't be broadcasted because no key was selected.", severity="error")
            return

        wrapper = await self.commands.perform_actions_on_transaction(
            content=transaction,
            sign_key=sign_key,
            broadcast=True,
        )
        if wrapper.error_occurred:
            # recompose key container in case fail of broadcast when transaction was already signed
            if transaction.is_signed:
                await self.key_container.recompose()
            self.notify("Transaction broadcast failed. Please try again.", severity="error")
            return

        self.notify(f"Transaction with ID '{transaction.calculate_transaction_id()}' successfully broadcasted!")
        self.profile.transaction.reset()
        self.profile.transaction_file_path = None
        self.app.trigger_profile_watchers()
        self.app.get_screen_from_current_stack(Dashboard).pop_until_active()

    async def _update_transaction_metadata(self) -> None:
        self.profile.transaction_file_path = None
        await self.commands.update_transaction_metadata(transaction=self.profile.transaction)
        self.app.trigger_profile_watchers()

    async def _rebuild_signatures_changed(self) -> None:
        await self.transaction_metadata_container.recompose()
        await self.key_container.recompose()

    def _get_key_to_sign(self) -> PublicKey:
        return self.key_container.selected_key

    def _update_bindings(self) -> None:
        if not self.profile.transaction:
            self.unbind(BROADCAST_TRANSACTION_BINDING_KEY)
            self.unbind(SAVE_TRANSACTION_TO_FILE_BINDING_KEY)
            self.unbind(REFRESH_TRANSACTION_METADATA_BINDING_KEY)
        else:
            self.bind(Binding(BROADCAST_TRANSACTION_BINDING_KEY, "broadcast", "Broadcast"))
            self.bind(Binding(SAVE_TRANSACTION_TO_FILE_BINDING_KEY, "save_to_file", "Save to file"))
            self.bind(Binding(REFRESH_TRANSACTION_METADATA_BINDING_KEY, "refresh_metadata", "Refresh metadata"))

    def _update_subtitle(self) -> None:
        subtitle = self.query_exactly_one(Subtitle)
        subtitle.update(self._create_subtitle_content())
        subtitle.display = bool(self.profile.transaction_file_path)

    async def _rebuild(self) -> None:
        await self.query_exactly_one(CartTable).rebuild()
        await self._rebuild_signatures_changed()
        await self.button_container.recompose()
        self._update_subtitle()
        self._update_bindings()

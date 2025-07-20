from __future__ import annotations

import contextlib
from copy import deepcopy
from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.events import Mount
from textual.widgets import Label, Select, Static

from clive.__private.core.formatters.humanize import humanize_relative_or_whole_path
from clive.__private.core.keys import PublicKey
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.settings import safe_settings
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs import (
    ConfirmInvalidateSignaturesDialog,
    SaveTransactionToFileDialog,
)
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.transaction_summary.cart_table import CartTable
from clive.__private.ui.screens.transaction_summary.transaction_metadata_container import (
    TransactionMetadataContainer,
    UpdateMetadataButton,
)
from clive.__private.ui.styling import colorize_path
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.select.safe_select import SafeSelect
from clive.exceptions import NoItemSelectedError

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widgets._select import NoSelection

    from clive.__private.core.profile import Profile


class AlreadySignedHint(Label):
    """
    Hint about the already signed transaction.

    Attributes:
        DEFAULT_CSS: Default CSS for styling the hint.
    """

    DEFAULT_CSS = """
    AlreadySignedHint {
        margin: 1 0;
        color: $success;
    }
    """

    def __init__(self) -> None:
        super().__init__("(This transaction is already signed)")


class BroadcastButton(CliveButton):
    """Button used to broadcasting transaction."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that broadcast button was pressed."""

    def __init__(self) -> None:
        super().__init__("Broadcast", binding=self.custom_bindings.transaction_summary.broadcast, variant="success")


class SaveButton(CliveButton):
    """Button used to save transaction to file."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that save button was pressed."""

    def __init__(self) -> None:
        super().__init__("Save to file", binding=self.custom_bindings.transaction_summary.save_transaction_to_file)


class LoadTransactionFromFileButton(CliveButton):
    """Button used to load transaction from file."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that load from file button was pressed."""

    def __init__(self) -> None:
        super().__init__("Load from file", binding=self.custom_bindings.app.load_transaction_from_file)


class ButtonContainer(Horizontal, CliveWidget):
    """Container for storing BroadcastButton, LoadTransactionFromFileButton and SaveButton."""

    def compose(self) -> ComposeResult:
        if self.profile.transaction:
            yield SaveButton()
            yield LoadTransactionFromFileButton()
            yield BroadcastButton()
        else:
            yield LoadTransactionFromFileButton()


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

        Raises:
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
    ]
    BIG_TITLE = "transaction summary"

    def __init__(self) -> None:
        super().__init__()
        self._update_bindings()
        self._previous_transaction = deepcopy(self.profile.transaction)
        self.watch(self.world, "profile_reactive", self._rebuild_on_transaction_change, init=False)
        self.watch(self.world, "node_reactive", self._update_bindings, init=False)

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

    @on(Mount)
    def focus_broadcast_button_if_possible(self) -> None:
        with contextlib.suppress(NoMatches):
            self.query_exactly_one(BroadcastButton).focus()

    @on(BroadcastButton.Pressed)
    async def action_broadcast(self) -> None:
        await self._broadcast()

    @on(SaveButton.Pressed)
    def action_save_transaction_to_file(self) -> None:
        try:
            sign_key = self._get_key_to_sign() if not self.profile.transaction.is_signed else None
        except NoItemSelectedError:
            sign_key = None

        self.app.push_screen(SaveTransactionToFileDialog(sign_key))

    @on(UpdateMetadataButton.Pressed)
    async def action_update_metadata(self) -> None:
        async def refresh() -> None:
            await self._update_transaction_metadata()
            await self._rebuild_signatures_changed()
            self._update_subtitle()

        async def update_metadata_cb(confirm: bool | None) -> None:  # noqa: FBT001
            if confirm:
                await refresh()

        if self.profile.transaction.is_signed:
            await self.app.push_screen(ConfirmInvalidateSignaturesDialog(), update_metadata_cb)
        else:
            await refresh()

    @on(LoadTransactionFromFileButton.Pressed)
    def load_transaction_from_file_by_button(self) -> None:
        self.app.action_load_transaction_from_file()

    @on(CartTable.Modified)
    async def handle_cart_update(self, event: CartTable.Modified) -> None:
        modified_transaction = event.transaction
        # Set the previous transaction before triggering watchers to avoid a full rebuild. This ensures only a
        # partial update is performed, as CartTable already handles the necessary changes internally.
        self._previous_transaction = deepcopy(modified_transaction)
        self.profile.transaction = modified_transaction
        self.profile.transaction_file_path = None
        self.app.trigger_profile_watchers()
        await self._rebuild_signatures_changed()
        await self.button_container.recompose()
        self._update_subtitle()
        self._update_bindings()

    def _create_subtitle_content(self) -> str:
        if self.profile.transaction_file_path:
            path = humanize_relative_or_whole_path(
                whole_path=self.profile.transaction_file_path,
                root_path=safe_settings.select_file_root_path,
            )
            return f"Loaded from {colorize_path(path)}"
        return ""

    async def _broadcast(self) -> None:
        from clive.__private.ui.screens.dashboard import Dashboard  # noqa: PLC0415

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
        await self.transaction_metadata_container.update_metadata_labels()
        await self.key_container.recompose()

    def _get_key_to_sign(self) -> PublicKey:
        return self.key_container.selected_key

    def _update_bindings(self) -> None:
        transaction_summary_bindings = self.app.custom_bindings.transaction_summary
        if not self.profile.transaction:
            self.unbind(transaction_summary_bindings.broadcast.key)
            self.unbind(transaction_summary_bindings.save_transaction_to_file.key)
            self.unbind(transaction_summary_bindings.update_metadata.key)
            return

        self.bind(transaction_summary_bindings.broadcast.create(show=False))
        self.bind(transaction_summary_bindings.save_transaction_to_file.create(description="Save to file", show=False))
        if self.node.cached.online_or_none:
            self.bind(transaction_summary_bindings.update_metadata.create(show=False))
        else:
            self.unbind(transaction_summary_bindings.update_metadata.key)

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

    async def _rebuild_on_transaction_change(self, profile: Profile) -> None:
        if self._previous_transaction != profile.transaction:
            await self._rebuild()
            self._previous_transaction = deepcopy(profile.transaction)

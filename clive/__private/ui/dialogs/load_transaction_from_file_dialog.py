from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal
from textual.widgets import DirectoryTree, Label

from clive.__private.core.commands.load_transaction import LoadTransactionError
from clive.__private.core.constants.tui.placeholders import PATH_PLACEHOLDER
from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.widgets.buttons import ConfirmOneLineButton
from clive.__private.ui.widgets.inputs.clive_input import CliveInput
from clive.__private.ui.widgets.inputs.path_input import PathInput
from clive.__private.ui.widgets.notice import Notice

if TYPE_CHECKING:
    from textual.app import ComposeResult


class LoadTransactionFromFileDialog(CliveActionDialog):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self) -> None:
        super().__init__("Choose a file to load the transaction", "Load file")
        self._file_path_input = PathInput(placeholder=PATH_PLACEHOLDER, validator_mode="is_file")

    def create_dialog_content(self) -> ComposeResult:
        if self.world.profile.transaction:
            yield Notice("Loading the transaction from the file will clear the current content of the cart.")
        with Horizontal(id="path-input-container"):
            yield self._file_path_input
        yield Label("Or select from the directory tree:", id="directory-tree-hint")
        yield DirectoryTree(str(Path.home()))

    @on(CliveInput.Submitted)
    async def _load_transaction_from_file_with_event(self) -> None:
        await self._load_transaction_from_file()

    @on(ConfirmOneLineButton.Pressed)
    async def _load_transaction_from_file_by_button(self) -> None:
        await self._load_transaction_from_file()

    @on(DirectoryTree.FileSelected)
    @on(DirectoryTree.DirectorySelected)
    def update_input_path(self, event: DirectoryTree.FileSelected) -> None:
        self._file_path_input.input.value = str(event.path)

    async def _load_transaction_from_file(self) -> bool:
        file_path = self._file_path_input.value_or_none()

        if file_path is None:
            return False

        try:
            loaded_transaction = (await self.commands.load_transaction_from_file(path=file_path)).result_or_raise
        except LoadTransactionError as error:
            self.notify(f"Error occurred while loading transaction from file: {error}", severity="error")
            return False

        if not loaded_transaction.is_tapos_set:
            self.notify("TaPoS metadata was not set, updating automatically...")
            self.profile.transaction_file_path = None
            await self.commands.update_transaction_metadata(transaction=self.profile.transaction)

        self.profile.transaction_file_path = file_path
        self.profile.transaction = loaded_transaction
        self.app.trigger_profile_watchers()

        return await self._perform_confirmation()

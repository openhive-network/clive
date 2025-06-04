from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.screens.config.manage_key_aliases.key_alias_base import NewKeyAliasBase
from clive.__private.ui.widgets.buttons.cancel_button import CancelOneLineButton
from clive.__private.ui.widgets.buttons.confirm_button import ConfirmOneLineButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton
from clive.__private.ui.widgets.inputs.clive_validated_input import FailedManyValidationError

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.keys.keys import PublicKey


class LoadFromFileButton(OneLineButton):
    """OneLineButton to load key from file."""

    class Pressed(OneLineButton.Pressed):
        """Used to identify exactly that LoadFromFileButton was pressed."""


class NewKeyAliasDialog(CliveActionDialog, NewKeyAliasBase):
    DEFAULT_CSS = """
    NewKeyAliasDialog {
        CliveDialogContent {
        width: 85%;
        #public-key, PublicKeyAliasInput {
            margin-top: 1;
            }
        }
    }
    """

    def __init__(self, public_key_to_match: str | PublicKey | None = None) -> None:
        super().__init__(border_title="Add new alias")
        self._public_key_to_match = public_key_to_match

    def _default_public_key_to_match(self) -> str | PublicKey | None:
        return self._public_key_to_match

    def create_dialog_content(self) -> ComposeResult:
        yield self._create_private_key_input()
        yield self._create_public_key_input()
        yield self._create_key_alias_input()

    def create_buttons_content(self) -> ComposeResult:
        yield LoadFromFileButton("Load from file", "success")
        yield ConfirmOneLineButton(self._confirm_button_text)
        yield CancelOneLineButton()

    @on(LoadFromFileButton.Pressed)
    def _load_from_file(self) -> None:
        from clive.__private.ui.dialogs import LoadKeyFromFileDialog

        self.app.push_screen(LoadKeyFromFileDialog(), self._load_key_into_input)

    async def _perform_confirmation(self) -> bool:
        return await self._save()

    def _load_key_into_input(self, loaded_private_key: str | None) -> None:
        if loaded_private_key is None:
            return

        self.private_key_input.input.value = loaded_private_key

    async def _save(self) -> bool:
        try:
            self._validate()
        except FailedManyValidationError:
            return False

        if not self._handle_key_alias_change(self._set_key_alias_to_import):
            return False
        await self._import_new_key()
        return True

    async def _import_new_key(self) -> None:
        await self.app.world.commands.sync_data_with_beekeeper()
        self.app.notify("New key alias was created.")
        self.app.trigger_profile_watchers()

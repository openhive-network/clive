from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on

from clive.__private.ui.dialogs import LoadKeyFromFileDialog
from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.key_alias_base import NewKeyAliasBase
from clive.__private.ui.widgets.buttons import LoadFromFileOneLineButton
from clive.__private.ui.widgets.buttons.cancel_button import CancelOneLineButton
from clive.__private.ui.widgets.buttons.confirm_button import ConfirmOneLineButton
from clive.__private.ui.widgets.inputs.clive_validated_input import FailedManyValidationError
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.keys.keys import PrivateKey, PublicKey


class NewKeyAliasDialog(CliveActionDialog, NewKeyAliasBase):
    DEFAULT_CSS = """
    NewKeyAliasDialog {
        CliveDialogContent {
            width: 85%;

        #public-key, PublicKeyAliasInput {
            margin-top: 1;
            }
        }

        SelectCopyPasteHint {
            margin: 1 1 0 1;
        }
    }
    """

    def __init__(self, public_key_to_match: PublicKey | None = None) -> None:
        super().__init__(border_title="Add new alias")
        self._public_key_to_match = public_key_to_match

    def _default_public_key_to_match(self) -> PublicKey | None:
        return self._public_key_to_match

    def create_dialog_content(self) -> ComposeResult:
        yield self._create_private_key_input()
        yield self._create_public_key_input()
        yield self._create_key_alias_input()
        yield SelectCopyPasteHint()

    def create_buttons_content(self) -> ComposeResult:
        yield LoadFromFileOneLineButton()
        yield ConfirmOneLineButton(self._confirm_button_text)
        yield CancelOneLineButton()

    @on(LoadFromFileOneLineButton.Pressed)
    def _load_from_file(self) -> None:
        def load_key_into_input(loaded_private_key: PrivateKey | None) -> None:
            if loaded_private_key is None:
                return

            self.private_key_input.input.value = loaded_private_key.value

        self.app.push_screen(LoadKeyFromFileDialog(), load_key_into_input)

    async def _perform_confirmation(self) -> bool:
        return await self._save()

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

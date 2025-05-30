from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.screens.config.manage_key_aliases.new_key_alias import NewKeyAlias

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.keys.keys import PublicKey


class NewKeyAliasDialog(CliveActionDialog, NewKeyAlias):
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

    def __init__(self, public_key_to_validate: str | PublicKey | None = None) -> None:
        CliveActionDialog.__init__(self, border_title="Add new alias")
        NewKeyAlias.__init__(self, public_key_to_validate)
        self.unbind("f6")  # unbind save action binding from NewKeyAlias base class

    def create_dialog_content(self) -> ComposeResult:
        yield self._key_input
        yield self._public_key_input
        yield self._key_alias_input

    async def _perform_confirmation(self) -> bool:
        return await self._save()

from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on

from clive.__private.ui.dialogs.confirm_action_dialog import ConfirmActionDialog

if TYPE_CHECKING:
    from clive.__private.core.keys import PublicKeyAliased


class RemoveKeyAliasDialog(ConfirmActionDialog):
    """Dialog to confirm if the user wants to remove key alias from profile."""

    def __init__(self, public_key: PublicKeyAliased) -> None:
        self._public_key = public_key
        super().__init__(
            border_title="Removing the key alias",
            confirm_question=(
                f"You are about to remove a `{self.key_alias}` key alias from the profile.\n"
                f"Are you sure you want to proceed?"
            ),
        )

    @property
    def key_alias(self) -> str:
        return self._public_key.alias

    @on(ConfirmActionDialog.Confirmed)
    def remove_key_alias(self) -> None:
        self.profile.keys.remove(self._public_key)
        self.notify(f"Key alias `{self.key_alias}` was removed.")
        self.app.trigger_profile_watchers()

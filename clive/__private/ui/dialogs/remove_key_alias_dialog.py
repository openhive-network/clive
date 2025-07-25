from __future__ import annotations

from clive.__private.ui.dialogs.confirm_action_dialog import ConfirmActionDialog


class RemoveKeyAliasDialog(ConfirmActionDialog):
    """
    Dialog to confirm if the user wants to remove key alias from profile.

    Args:
        key_alias: Alias of key that is about to be removed.

    Raises:
        KeyNotFoundError: When key with given alias was not found in the profile.
    """

    def __init__(self, key_alias: str) -> None:
        self._public_key_aliased = self.profile.keys.get_from_alias(key_alias)
        super().__init__(
            border_title="Removing the key alias",
            confirm_question=(
                f"You are about to remove a `{self._public_key_aliased.alias}` key alias from the profile.\n"
                f"Are you sure you want to proceed?"
            ),
        )

    async def _perform_confirmation(self) -> bool:
        self.profile.keys.remove(self._public_key_aliased)
        self.notify(f"Key alias `{self._public_key_aliased.alias}` was removed.")
        self.app.trigger_profile_watchers()
        return True

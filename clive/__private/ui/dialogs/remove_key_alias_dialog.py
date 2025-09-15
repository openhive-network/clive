from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.dialogs.confirm_action_dialog import ConfirmActionDialog

if TYPE_CHECKING:
    from clive.__private.core.keys.keys import PublicKeyAliased


class RemoveKeyAliasDialog(ConfirmActionDialog):
    """
    Dialog to confirm if the user wants to remove key alias or many aliases from profile.

    Args:
        *key_aliases: Key aliases that are about to be removed.

    Raises:
        KeyNotFoundError: When given key alias is not found in the profile.
    """

    def __init__(self, *key_aliases: str | PublicKeyAliased) -> None:
        self._keys_to_remove = self.get_keys_to_remove(*key_aliases)

        super().__init__(border_title="Removing the key alias", confirm_question=self._get_confirm_question())

    @property
    def is_removing_single_alias(self) -> bool:
        return len(self._keys_to_remove) == 1

    def get_keys_to_remove(self, *key_aliases: str | PublicKeyAliased) -> list[PublicKeyAliased]:
        """
        Get all the aliased key instances that are about to be removed.

        Args:
            *key_aliases: Key aliases that are about to be removed.

        Raises:
            KeyNotFoundError: When given key alias is not found in the profile.

        Returns:
            Aliased keys to remove.
        """
        return [self.profile.keys.get_from_alias(item) for item in key_aliases]

    async def _perform_confirmation(self) -> bool:
        self.profile.keys.remove(*self._keys_to_remove)
        self.notify(self._get_notify_text())
        self.app.trigger_profile_watchers()
        return True

    def _get_confirm_question(self) -> str:
        keys_to_remove = self._keys_to_remove
        if self.is_removing_single_alias:
            key_alias = keys_to_remove[0].alias
            part_of_question = f"a `{key_alias}` key alias"
        else:
            aliases = [key.alias for key in keys_to_remove]
            part_of_question = f"{', '.join(f'`{alias}`' for alias in aliases)} key aliases"

        return f"You are about to remove {part_of_question} from the profile.\nAre you sure you want to proceed?"

    def _get_notify_text(self) -> str:
        if self.is_removing_single_alias:
            key_alias = self._keys_to_remove[0].alias
            return f"Key alias `{key_alias}` was removed."
        return "Many key aliases were removed."

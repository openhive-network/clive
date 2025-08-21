from __future__ import annotations

from clive.__private.ui.dialogs.confirm_action_dialog import ConfirmActionDialog


class RemoveKeyAliasDialog(ConfirmActionDialog):
    """
    Dialog to confirm if the user wants to remove key alias or many aliases from profile.

    Args:
        *key_aliases: Aliases of keys that are about to be removed.

    Raises:
        KeyNotFoundError: When key with given alias was not found in the profile.
    """

    def __init__(self, *key_aliases: str) -> None:
        self._public_keys_aliased = [self.profile.keys.get_from_alias(key_alias) for key_alias in key_aliases]
        self._single_alias_removal = len(self._public_keys_aliased) == 1
        part_of_confirm_question = (
            f"a `{next(iter(self._public_keys_aliased)).alias} key alias`"
            if self._single_alias_removal
            else "many key aliases"
        )
        super().__init__(
            border_title="Removing the key alias",
            confirm_question=(
                f"You are about to remove {part_of_confirm_question} from the profile.\n"
                f"Are you sure you want to proceed?"
            ),
        )

    async def _perform_confirmation(self) -> bool:
        notify_text = (
            f"Key alias `{next(iter(self._public_keys_aliased)).alias}` was removed."
            if self._single_alias_removal
            else "Many key aliases were removed."
        )
        self.profile.keys.remove(*self._public_keys_aliased)
        self.notify(notify_text)
        self.app.trigger_profile_watchers()
        return True

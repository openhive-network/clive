from __future__ import annotations

from clive.__private.core.keys import PublicKeyAliased
from clive.__private.ui.dialogs.confirm_action_dialog import ConfirmActionDialog
from wax.models.basic import PublicKey


class RemoveKeyAliasDialog(ConfirmActionDialog):
    """Dialog to confirm if the user wants to remove key alias from profile."""

    def __init__(self, public_key: PublicKey | PublicKeyAliased) -> None:
        if isinstance(public_key, PublicKey):
            # find corresponding aliased key for given value:
            for aliased_key in self.profile.keys:
                if aliased_key.value == public_key:
                    public_key = aliased_key

        assert isinstance(public_key, PublicKeyAliased), "Public key has to be in PublicKeyAliased type at this point!"
        self._public_key = public_key
        super().__init__(
            border_title="Removing the key alias",
            confirm_question=(
                f"You are about to remove key {self._public_key.value} aliased `{self.key_alias}` from the profile.\n"
                f"Are you sure you want to proceed?"
            ),
        )

    @property
    def key_alias(self) -> str:
        return self._public_key.alias

    async def _perform_confirmation(self) -> bool:
        self.profile.keys.remove(self._public_key)
        self.notify(f"Key alias `{self.key_alias}` was removed.")
        self.app.trigger_profile_watchers()
        return True

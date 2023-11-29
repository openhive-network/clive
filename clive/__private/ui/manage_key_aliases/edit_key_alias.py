from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.ui.manage_key_aliases.widgets.key_alias_form import KeyAliasForm
from clive.exceptions import AliasAlreadyInUseFormError

if TYPE_CHECKING:
    from clive.__private.core.keys import PublicKeyAliased
    from clive.__private.core.profile_data import ProfileData


class EditKeyAlias(KeyAliasForm):
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
        Binding("f10", "save", "Save"),
    ]

    def __init__(self, public_key: PublicKeyAliased) -> None:
        self.public_key = public_key
        super().__init__()

    @property
    def context(self) -> ProfileData:
        return self.app.world.profile_data

    def action_save(self) -> None:
        self._save()

    def _save(self) -> None:
        old_alias = self.public_key.alias
        new_alias = self._key_alias_raw

        if old_alias == new_alias:
            self.notify("No changes to save", severity="warning")
            return

        if not self._validate_with_notification():
            return

        self.app.world.profile_data.working_account.keys.rename(old_alias, new_alias)

        self.app.trigger_profile_data_watchers()
        self.app.post_message_to_screen("ManageKeyAliases", self.Changed())
        self.app.pop_screen()
        self.notify(f"Key alias `{self.public_key.alias}` was edited.")

    def _validate(self) -> None:
        """
        Validate the form data.

        Raises
        ------
        AliasAlreadyInUseFormError: if alias is already in use.
        """
        if not self.context.working_account.keys.is_public_alias_available(self._key_alias_raw):
            raise AliasAlreadyInUseFormError(self._key_alias_raw)

    def _title(self) -> str:
        return "edit alias"

    def _default_key_alias_name(self) -> str:
        return self.public_key.alias

    def _default_public_key(self) -> str:
        return self.public_key.value

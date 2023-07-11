from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.ui.app_messages import ProfileDataUpdated
from clive.__private.ui.manage_authorities.widgets.authority_form import AuthorityForm
from clive.__private.ui.widgets.notification import Notification
from clive.exceptions import AliasAlreadyInUseFormError

if TYPE_CHECKING:
    from clive.__private.core.keys import PublicKeyAliased
    from clive.__private.core.profile_data import ProfileData


class EditAuthority(AuthorityForm):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f10", "save", "Save"),
    ]

    def __init__(self, authority: PublicKeyAliased) -> None:
        self.authority = authority
        super().__init__()

    @property
    def context(self) -> ProfileData:
        return self.app.world.profile_data

    def action_save(self) -> None:
        self._save()

    def _save(self) -> None:
        old_alias = self.authority.alias
        new_alias = self._key_alias_raw

        if old_alias == new_alias:
            Notification("No changes to save", category="warning").show()
            return

        if not self._validate_with_notification():
            return

        self.app.world.profile_data.working_account.keys.rename(old_alias, new_alias)

        self.app.post_message_to_everyone(ProfileDataUpdated())
        self.app.post_message_to_screen("ManageAuthorities", self.AuthoritiesChanged())
        self.app.pop_screen()
        Notification(f"Authority `{self.authority.alias}` was edited.", category="success").show()

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
        return "edit authority"

    def _default_authority_name(self) -> str:
        return self.authority.alias

    def _default_public_key(self) -> str:
        return self.authority.value

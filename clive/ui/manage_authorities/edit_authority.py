from __future__ import annotations

from typing import TYPE_CHECKING

from clive.ui.manage_authorities.widgets.authority_form import AuthorityForm

if TYPE_CHECKING:
    from clive.storage.mock_database import PrivateKey


class EditAuthority(AuthorityForm):
    def __init__(self, authority: PrivateKey, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        self.authority = authority
        super().__init__(name, id, classes)

    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        idx = self.app.profile_data.active_account.keys.index(self.authority)
        self.app.profile_data.active_account.keys[idx] = event.authority
        self.app.update_reactive("profile_data")

    def _title(self) -> str:
        return "edit authority"

    def _default_authority_name(self) -> str:
        return self.authority.key_name

    def _default_raw_authority(self) -> str:
        return self.authority.key

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.storage.mock_database import PrivateKey
from clive.__private.ui.manage_authorities.widgets.authority_form import AuthorityForm
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from clive.__private.storage.mock_database import PrivateKeyAlias


class EditAuthority(AuthorityForm):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "load_from_file", "Load from file"),
        Binding("f10", "save", "Save"),
    ]

    def __init__(self, authority: PrivateKeyAlias) -> None:
        self.authority = authority
        super().__init__()

    def action_save(self) -> None:
        self._save()

    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        idx = self.app.profile_data.working_account.keys.index(self.authority)
        self.app.profile_data.working_account.keys[idx] = event.private_key
        self.app.update_reactive("profile_data")

        self.app.pop_screen()
        Notification(f"Authority `{event.private_key.key_name}` was edited.", category="success").show()
        self.app.post_message_to_screen("ManageAuthorities", self.AuthoritiesChanged())

    def _title(self) -> str:
        return "edit authority"

    def _default_authority_name(self) -> str:
        return self.authority.key_name

    def _default_key(self) -> str:
        if isinstance(self.authority, PrivateKey):
            return self.authority.key
        return super()._default_key()

    def _default_file_path(self) -> str:
        if isinstance(self.authority, PrivateKey) and self.authority.file_path:
            return str(self.authority.file_path)
        return super()._default_key()

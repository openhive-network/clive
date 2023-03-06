from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.ui.manage_authorities.widgets.authority_form import AuthorityForm
from clive.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from clive.storage.mock_database import PrivateKey


class EditAuthority(AuthorityForm):
    BINDINGS = [
        Binding("escape", "pop_screen", "Authorities"),
    ]

    def __init__(self, authority: PrivateKey) -> None:
        self.authority = authority
        super().__init__()

    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        idx = self.app.profile_data.active_account.keys.index(self.authority)
        self.app.profile_data.active_account.keys[idx] = event.private_key
        self.app.update_reactive("profile_data")

        self.app.pop_screen()
        Notification(f"Authority `{event.private_key.key_name}` was edited.", category="success").show()
        self.app.post_message_to_screen("ManageAuthorities", self.AuthoritiesChanged(self))

    def _title(self) -> str:
        return "edit authority"

    def _default_authority_name(self) -> str:
        return self.authority.key_name

    def _default_file_path(self) -> str:
        return str(self.authority.file_path) if self.authority.file_path else ""

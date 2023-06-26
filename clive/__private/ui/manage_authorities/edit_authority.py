from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.ui.manage_authorities.widgets.authority_form import AuthorityForm
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from clive.__private.core.keys.keys import PublicKeyAliased
    from clive.__private.core.profile_data import ProfileData


class EditAuthority(AuthorityForm):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "load_from_file", "Load from file"),
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

    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        # TODO: We should allow for alias editing
        self.app.world.update_reactive("profile_data")

        self.app.pop_screen()
        Notification(f"Authority `{event.private_key.alias}` was edited.", category="success").show()
        self.app.post_message_to_screen("ManageAuthorities", self.AuthoritiesChanged())

    def _title(self) -> str:
        return "edit authority"

    def _default_authority_name(self) -> str:
        return self.authority.alias

    def _default_public_key(self) -> str:
        return self.authority.value

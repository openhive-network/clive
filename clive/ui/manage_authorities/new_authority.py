from __future__ import annotations

from textual.binding import Binding

from clive.ui.manage_authorities.widgets.authority_form import AuthorityForm
from clive.ui.shared.form_screen import FormScreen
from clive.ui.widgets.notification import Notification


class NewAuthorityBase(AuthorityForm):
    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        self.app.profile_data.active_account.keys.append(event.private_key)
        self.app.update_reactive("profile_data")

        self.app.pop_screen()
        Notification(f"New authority `{event.private_key.key_name}` was created.", category="success").show()
        self.app.post_message_to_screen("ManageAuthorities", self.AuthoritiesChanged(self))

    def _title(self) -> str:
        return "define keys"


class NewAuthority(NewAuthorityBase):
    BINDINGS = [
        Binding("escape", "pop_screen", "Authorities"),
    ]


class NewAuthorityForm(NewAuthorityBase, FormScreen):
    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        event.prevent_default()

        self.app.profile_data.active_account.keys.append(event.private_key)
        self.app.update_reactive("profile_data")

        self._owner.action_next_screen()
        Notification(f"New authority `{event.private_key.key_name}` was created.", category="success").show()

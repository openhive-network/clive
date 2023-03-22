from __future__ import annotations

from textual.binding import Binding

from clive.ui.manage_authorities.widgets.authority_form import AuthorityForm
from clive.ui.shared.form_screen import FormScreen
from clive.ui.widgets.notification import Notification


class NewAuthorityBase(AuthorityForm):
    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        self.app.profile_data.working_account.keys.append(event.private_key)
        self.app.update_reactive("profile_data")

        self.app.pop_screen()
        Notification(f"New authority `{event.private_key.key_name}` was created.", category="success").show()
        self.app.post_message_to_screen("ManageAuthorities", self.AuthoritiesChanged())

    def _title(self) -> str:
        return "define keys"


class NewAuthority(NewAuthorityBase):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "load_from_file", "Load from file"),
        Binding("f10", "save", "Save"),
    ]

    def action_save(self) -> None:
        self._save()


class NewAuthorityForm(NewAuthorityBase, FormScreen):
    BINDINGS = [
        Binding("f2", "load_from_file", "Load from file"),
    ]

    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        event.prevent_default()

        self.app.profile_data.working_account.keys.append(event.private_key)
        self.app.update_reactive("profile_data")

        self._owner.action_next_screen()
        Notification(f"New authority `{event.private_key.key_name}` was created.", category="success").show()

    def action_next_screen(self) -> None:
        if not self._get_key():  # this (NewAuthorityForm) step is optional, so we can skip it when no key is provided
            super().action_next_screen()
            return

        self._save()

    def _subtitle(self) -> str:
        return "(Optional step, could be done later)"

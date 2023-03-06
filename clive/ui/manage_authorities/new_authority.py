from __future__ import annotations

from textual.binding import Binding

from clive.ui.manage_authorities.widgets.authority_form import AuthorityForm
from clive.ui.shared.form_screen import FormScreen


class NewAuthorityBase(AuthorityForm):
    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        self.app.profile_data.active_account.keys.append(event.authority)
        self.app.update_reactive("profile_data")

    def _title(self) -> str:
        return "create authority"


class NewAuthority(NewAuthorityBase):
    BINDINGS = [
        Binding("escape", "pop_screen", "Authorities"),
    ]


class NewAuthorityForm(NewAuthorityBase, FormScreen):
    pass

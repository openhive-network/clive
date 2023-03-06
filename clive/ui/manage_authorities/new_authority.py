from __future__ import annotations


from clive.ui.manage_authorities.widgets.authority_form import AuthorityForm
from clive.ui.shared.form_screen import FormScreen


class NewAuthority(AuthorityForm):
    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        self.app.profile_data.active_account.keys.append(event.authority)
        self.app.update_reactive("profile_data")

    def _title(self) -> str:
        return "create authority"


class NewAuthorityForm(NewAuthority, FormScreen):
    """Form used for creating a new authority."""

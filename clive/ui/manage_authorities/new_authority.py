from __future__ import annotations

from typing import TYPE_CHECKING

from clive.ui.manage_authorities.widgets.authority_form import AuthorityForm
from clive.ui.shared.form_screen import FormScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class NewAuthority(FormScreen):
    def create_main_panel(self) -> ComposeResult:
        yield AuthorityForm("create authority")

    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        self.app.profile_data.active_account.keys.append(event.authority)
        self.app.update_reactive("profile_data")

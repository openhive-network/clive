from __future__ import annotations

from typing import TYPE_CHECKING

from clive.ui.manage_authorities.widgets.authority_form import AuthorityForm
from clive.ui.shared.base_screen import BaseScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.storage.mock_database import PrivateKey


class EditAuthority(BaseScreen):
    def __init__(self, authority: PrivateKey) -> None:
        self.authority = authority
        super().__init__()

    def create_main_panel(self) -> ComposeResult:
        yield AuthorityForm("edit authority", existing_authority=self.authority)

    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        idx = self.app.profile_data.active_account.keys.index(self.authority)
        self.app.profile_data.active_account.keys[idx] = event.authority
        self.app.update_reactive("profile_data")

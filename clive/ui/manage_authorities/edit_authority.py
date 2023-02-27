from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from clive.ui.manage_authorities.widgets.authority_form import AuthorityForm
from clive.ui.shared.base_screen import BaseScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.storage.mock_database import PrivateKey


class EditAuthorities(BaseScreen):
    def __init__(self, authority: PrivateKey, callback: Callable[[], None]) -> None:
        self.authority = authority
        self.callback = callback
        super().__init__()

    def create_main_panel(self) -> ComposeResult:
        yield AuthorityForm(self.authority, self.callback, "edit authority")

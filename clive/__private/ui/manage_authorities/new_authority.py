from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.storage.contextual import Contextual
from clive.__private.storage.mock_database import ProfileData
from clive.__private.ui.app_messages import ProfileDataUpdated
from clive.__private.ui.manage_authorities.widgets.authority_form import AuthorityForm
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.notification import Notification
from clive.exceptions import FormValidationError

if TYPE_CHECKING:
    from clive.__private.ui.shared.form import Form


class NewAuthorityBase(AuthorityForm, Contextual[ProfileData], ABC):
    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        self.context.working_account.keys.append(event.private_key)
        self.post_message(ProfileDataUpdated())

    def _title(self) -> str:
        return "define keys"


class NewAuthority(NewAuthorityBase):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "load_from_file", "Load from file"),
        Binding("f10", "save", "Save"),
    ]

    @property
    def context(self) -> ProfileData:
        return self.app.profile_data

    def on_authority_form_saved(self, _: AuthorityForm.Saved) -> None:
        self.app.post_message_to_screen("ManageAuthorities", self.AuthoritiesChanged())
        self.app.pop_screen()

    def action_save(self) -> None:
        try:
            if self._is_key_provided():
                self._save()
                Notification("New authority was created.", category="success").show()
        except FormValidationError:
            Notification("Failed the validation process! Could not continue", category="error").show()


class NewAuthorityForm(NewAuthorityBase, FormScreen[ProfileData]):
    BINDINGS = [
        Binding("f2", "load_from_file", "Load from file"),
    ]

    def __init__(self, owner: Form[ProfileData]) -> None:
        super().__init__(owner=owner)

    def apply_and_validate(self) -> None:
        if self._is_key_provided():
            self._save()  # this (NewAuthorityForm) step is optional, so we can skip it when no key is provided

    def _subtitle(self) -> str:
        return "(Optional step, could be done later)"

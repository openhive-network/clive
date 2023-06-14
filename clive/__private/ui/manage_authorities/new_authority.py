from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.core.profile_data import ProfileData
from clive.__private.logger import logger
from clive.__private.storage.mock_database import PublicKeyAliased
from clive.__private.ui.app_messages import ProfileDataUpdated
from clive.__private.ui.manage_authorities.widgets.authority_form import AuthorityForm
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from clive.__private.ui.shared.form import Form


class NewAuthorityBase(AuthorityForm, ABC):
    BINDINGS = [
        Binding("f2", "load_from_file", "Load from file"),
    ]

    def _title(self) -> str:
        return "define keys"


class NewAuthority(NewAuthorityBase):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f10", "save", "Save"),
    ]

    @property
    def context(self) -> ProfileData:
        return self.app.world.profile_data

    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        imported = self.app.world.commands.import_key(alias=event.key_alias, wif=event.private_key)
        self.app.world.profile_data.working_account.keys.append(
            PublicKeyAliased(alias=event.key_alias, value=imported.value)
        )

        self.app.post_message_to_everyone(ProfileDataUpdated())
        self.app.post_message_to_screen("ManageAuthorities", self.AuthoritiesChanged())
        self.app.pop_screen()
        Notification("New authority was created.", category="success").show()

    def action_save(self) -> None:
        self._save()


class NewAuthorityForm(NewAuthorityBase, FormScreen[ProfileData]):
    def __init__(self, owner: Form[ProfileData]) -> None:
        super().__init__(owner=owner)

    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        self.context.working_account.keys_to_import = {event.key_alias: event.private_key}
        logger.debug("New authority is waiting to be imported...")

    def apply_and_validate(self) -> None:
        if self._is_key_provided():  # NewAuthorityForm step is optional, so we can skip it when no key is provided
            self._save(reraise_exception=True)

    def _subtitle(self) -> str:
        return "(Optional step, could be done later)"

from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.profile import Profile
from clive.__private.ui.forms.create_profile.create_profile_form_screen import CreateProfileFormScreen
from clive.__private.ui.forms.create_profile.new_key_alias_form_screen import NewKeyAliasFormScreen
from clive.__private.ui.forms.create_profile.set_account_form_screen import SetAccountFormScreen
from clive.__private.ui.forms.create_profile.welcome_form_screen import CreateProfileWelcomeFormScreen
from clive.__private.ui.forms.form import Form

if TYPE_CHECKING:
    from collections.abc import Iterator

    from clive.__private.ui.forms.form_screen import FormScreenBase


class CreateProfileForm(Form):
    async def initialize(self) -> None:
        await self.world.create_new_profile("temp_name")
        self.profile.skip_saving()

    async def cleanup(self) -> None:
        await self.world.switch_profile(None)
        self.app.call_later(lambda: self.app.remove_mode("create_profile"))

    def compose_form(self) -> Iterator[type[FormScreenBase]]:
        if not Profile.is_any_profile_saved():
            yield CreateProfileWelcomeFormScreen
        yield CreateProfileFormScreen
        yield SetAccountFormScreen
        yield NewKeyAliasFormScreen

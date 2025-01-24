from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.profile import Profile
from clive.__private.ui.forms.create_profile.create_profile_form_screen import CreateProfileFormScreen
from clive.__private.ui.forms.create_profile.new_key_alias_form_screen import NewKeyAliasFormScreen
from clive.__private.ui.forms.create_profile.set_account_form_screen import SetAccountFormScreen
from clive.__private.ui.forms.create_profile.welcome_form_screen import CreateProfileWelcomeFormScreen
from clive.__private.ui.forms.form import Form, ScreenBuilder

if TYPE_CHECKING:
    from collections.abc import Iterator


class CreateProfileForm(Form):
    async def initialize(self) -> None:
        await self.world.create_new_profile("temp_name")
        self.profile.skip_saving()

    async def cleanup(self) -> None:
        await self.world.switch_profile(None)
        self.app.call_later(lambda: self.app.remove_mode("create_profile"))

    def register_screen_builders(self) -> Iterator[ScreenBuilder]:
        if not Profile.is_any_profile_saved():
            yield CreateProfileWelcomeFormScreen
        yield CreateProfileFormScreen
        yield SetAccountFormScreen
        yield NewKeyAliasFormScreen

    def _skip_during_push_screen(self) -> list[ScreenBuilder]:
        screens_to_skip: list[ScreenBuilder] = []

        # skip NewKeyAliasForm if there is no working account set
        if not self.profile.accounts.has_working_account:
            screens_to_skip.append(NewKeyAliasFormScreen)

        return screens_to_skip

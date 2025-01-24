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

    def register_screens(self) -> Iterator[type[FormScreenBase]]:
        if not Profile.is_any_profile_saved():
            yield CreateProfileWelcomeFormScreen
        yield CreateProfileFormScreen
        yield SetAccountFormScreen
        yield NewKeyAliasFormScreen

    async def exit_form(self) -> None:
        # when this form is displayed during onboarding, there is no previous screen to go back to
        # so this method won't be called
        await self.app.switch_mode("unlock")
        await self.app.remove_mode("create_profile")

    async def finish_form(self) -> None:
        async def _finish() -> None:
            async def _handle_modes() -> None:
                await self.app.switch_mode("dashboard")
                self.app.remove_mode("create_profile")
                self.app.remove_mode("unlock")

            self.add_post_action(self.app.update_alarms_data_asap_on_newest_node_data)
            await self.execute_post_actions()
            await _handle_modes()
            self.profile.enable_saving()
            self.profile.save()

        # Has to be done in a separate task to avoid deadlock. More: https://github.com/Textualize/textual/issues/5008
        self.run_worker(_finish())

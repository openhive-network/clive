from __future__ import annotations

from clive.__private.core.profile import Profile
from clive.__private.ui.forms.create_profile.new_key_alias_form_screen import NewKeyAliasFormScreen
from clive.__private.ui.forms.create_profile.profile_credentials_form_screen import ProfileCredentialsFormScreen
from clive.__private.ui.forms.create_profile.set_account_form_screen import SetAccountFormScreen
from clive.__private.ui.forms.create_profile.welcome_form_screen import WelcomeFormScreen
from clive.__private.ui.forms.form import ComposeFormResult, Form


class CreateProfileForm(Form):
    async def initialize(self) -> None:
        await self.world.create_new_profile("temp_name", skip_saving=True)

    async def cleanup(self) -> None:
        await self.world.switch_profile(None)

    def compose_form(self) -> ComposeFormResult:
        if not Profile.is_any_profile_saved():
            yield WelcomeFormScreen
        yield ProfileCredentialsFormScreen
        yield SetAccountFormScreen
        yield NewKeyAliasFormScreen

    async def exit_form(self) -> None:
        # when this form is displayed during onboarding, there is no previous screen to go back to
        # so this method won't be called

        async def impl() -> None:
            await self.app.switch_mode_with_reset("unlock")

        # Has to be done in a separate task to avoid deadlock.
        # More: https://github.com/Textualize/textual/issues/5008
        self.app.run_worker_with_screen_remove_guard(impl())

    async def finish_form(self) -> None:
        async def impl() -> None:
            await self.execute_post_actions()
            self.profile.enable_saving()
            await self.commands.save_profile()
            await self.app._switch_mode_into_unlocked()

        # Has to be done in a separate task to avoid deadlock.
        # More: https://github.com/Textualize/textual/issues/5008
        self.app.run_worker_with_screen_remove_guard(impl())
